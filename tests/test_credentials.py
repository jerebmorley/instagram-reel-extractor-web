import pytest
from cryptography.fernet import Fernet

from sorteos.credentials import CredentialError, load_token, save_token


def test_roundtrip_and_wrong_key(tmp_path, monkeypatch):
    path = tmp_path / "cuenta"
    monkeypatch.setenv("SORTEOS_FERNET_KEY", Fernet.generate_key().decode())
    save_token(path, "synthetic-secret")
    assert b"synthetic-secret" not in path.read_bytes()
    assert path.stat().st_mode & 0o077 == 0
    assert load_token(path) == "synthetic-secret"
    with pytest.raises(CredentialError):
        save_token(path, "replacement", "2000-01-01")
    assert load_token(path) == "synthetic-secret"
    monkeypatch.setenv("SORTEOS_FERNET_KEY", Fernet.generate_key().decode())
    with pytest.raises(CredentialError):
        load_token(path)
