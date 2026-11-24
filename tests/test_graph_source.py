from unittest.mock import Mock

import pytest

from sorteos.graph import GraphError
from sorteos.graph_source import GraphSource


def row(id):
    return {"id": id, "text": "demo", "timestamp": "2026-01-01T00:00:00Z"}


def test_independent_reply_and_root_cursors():
    graph = Mock()
    more = {"next": "ignored", "cursors": {"after": "opaque"}}
    graph.read.side_effect = [
        {"data": [row("1")], "paging": more},
        {"data": [], "paging": more},
        {"data": [row("3")]},
        {"data": [row("2")]},
        {"data": []},
    ]
    assert [(r.id, r.parent_id) for r in GraphSource(graph, "100")] == [
        ("1", None),
        ("3", "1"),
        ("2", None),
    ]
    assert [(c.args[0], c.kwargs.get("after")) for c in graph.read.call_args_list] == [
        ("100/comments", None),
        ("1/replies", None),
        ("1/replies", "opaque"),
        ("100/comments", "opaque"),
        ("2/replies", None),
    ]


def test_cycle_stops():
    graph = Mock()
    graph.read.return_value = {
        "data": [],
        "paging": {"next": "ignored", "cursors": {"after": "same"}},
    }
    with pytest.raises(GraphError, match="repetido"):
        list(GraphSource(graph, "100"))
    assert graph.read.call_count == 2
