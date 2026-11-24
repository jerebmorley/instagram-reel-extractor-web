import pytest

from sorteos.mentions import mentions


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("(@Ana.P), @ANA.p... y @b_2!", ("ana.p", "b_2")),
        (
            "ana+demo@correo.ar https://sitio.ar/@hola www.sitio.ar/?q=@x sitio.ar/@otro @bien",
            ("bien",),
        ),
        ("@аna @anа @ana\u0301 ＠ana @a..b", ()),
        ("@" + "a" * 31, ()),
        ("👍@UNO,@dos", ("uno", "dos")),
    ],
)
def test_mentions(text, expected):
    assert mentions(text) == expected
