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
