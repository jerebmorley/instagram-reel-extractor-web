from datetime import datetime, timedelta, timezone

import pytest

from sorteos.models import Comment


def test_reply_keeps_unknown_author_and_normalizes_instant():
    local = datetime(2026, 11, 24, 21, tzinfo=timezone(-timedelta(hours=3)))
    reply = Comment("reply", "media", "  @Demo  ", local, parent_id="root")
    assert reply.created_at == datetime(2026, 11, 25, tzinfo=timezone.utc)
    assert reply.created_at.tzinfo is timezone.utc
    assert reply.text == "  @Demo  "
    assert reply.username is None and reply.author_id is None
    assert reply.parent_id == "root"


@pytest.mark.parametrize(
    "change",
    [
        {"id": ""},
        {"media_id": None},
        {"parent_id": "root"},
        {"username": " "},
        {"created_at": datetime(2026, 11, 24)},
        {"text": None},
    ],
)
def test_incomplete_or_inconsistent_record(change):
    fields = dict(
        id="root", media_id="media", text="", created_at=datetime.now(timezone.utc)
    )
    with pytest.raises(ValueError):
        Comment(**(fields | change))


def test_root_with_username_only():
    root = Comment("root", "media", "", datetime.now(timezone.utc), username="Demo")
    assert root.parent_id is None and root.author_id is None
    assert root.username == "Demo"
