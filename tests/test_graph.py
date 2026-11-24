import io
from unittest.mock import patch

import pytest

from sorteos.graph import Graph, GraphError


def test_profile_uses_header_and_limits_output():
    with patch("sorteos.graph.HTTPSConnection") as factory:
        connection = factory.return_value
        response = io.BytesIO(b'{"id":"1","username":"demo","extra":"unused"}')
        response.status = 200
        connection.getresponse.return_value = response
        assert Graph("v25.0", "fake").profile() == {"id": "1", "username": "demo"}
        connection.request.assert_called_once_with(
            "GET",
            "/v25.0/me?fields=id%2Cusername",
            headers={"Authorization": "Bearer fake"},
        )


def test_failure_does_not_echo_response():
    with patch("sorteos.graph.HTTPSConnection") as factory:
        factory.return_value.getresponse.return_value.status = 403
        with pytest.raises(GraphError, match="HTTP 403") as error:
            Graph("v25.0", "synthetic-secret").profile()
        assert "synthetic-secret" not in str(error.value)


def test_sample_keeps_partial_pages_and_missing_fields_visible():
    graph = Graph("v25.0", "fake")
    with patch.object(
        graph,
        "read",
        side_effect=[
            {"data": [{"id": "2", "text": "privado"}], "paging": {"next": "sensible"}},
            {"data": [{"id": "3", "username": "persona"}]},
        ],
    ) as read:
        result = graph.comments("1")
        assert [c.args[0] for c in read.call_args_list] == ["1/comments", "2/replies"]
    assert result["hay_mas"]
    assert result["comentarios"] == [
        {
            "campos_presentes": ["id", "text"],
            "respuestas": [["id", "username"]],
            "hay_mas_respuestas": False,
        }
    ]


def test_empty_media():
    graph = Graph("v25.0", "fake")
    with patch.object(graph, "read", return_value={"data": []}):
        assert graph.media() == {"publicaciones": [], "hay_mas": False}


@pytest.mark.parametrize("budget,expected", [(2, 2), (9, 3)])
def test_transient_attempts_are_bounded(budget, expected):
    with (
        patch("sorteos.graph.HTTPSConnection") as factory,
        patch("sorteos.graph.time.sleep") as sleep,
    ):
        factory.return_value.getresponse.side_effect = TimeoutError()
        with pytest.raises(GraphError):
            Graph("v25.0", "fake", request_budget=budget).profile()
        assert factory.return_value.request.call_count == expected
        assert sleep.call_count == expected - 1


def test_rate_limit_stops_without_retry():
    with patch("sorteos.graph.HTTPSConnection") as factory:
        factory.return_value.getresponse.return_value.status = 429
        with pytest.raises(GraphError, match="429"):
            Graph("v25.0", "fake").profile()
        assert factory.return_value.request.call_count == 1


def test_retry_success_charges_shared_budget():
    with (
        patch("sorteos.graph.HTTPSConnection") as factory,
        patch("sorteos.graph.time.sleep"),
    ):
        response = io.BytesIO(b'{"id":"1","username":"demo"}')
        response.status = 200
        factory.return_value.getresponse.side_effect = [TimeoutError(), response]
        graph = Graph("v25.0", "fake", request_budget=2)
        assert graph.profile()["id"] == "1"
        with pytest.raises(GraphError, match="agotado"):
            graph.profile()
        assert factory.return_value.request.call_count == 2
