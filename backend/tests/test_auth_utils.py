import os

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")

from routes.auth import hash_password, verify_password


def test_hash_password_generates_non_plaintext_value() -> None:
    password = "SuperStrongPassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert isinstance(hashed, str)
    assert len(hashed) > 20


def test_verify_password_accepts_valid_password() -> None:
    password = "AnotherStrongPassword!"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_rejects_invalid_password() -> None:
    hashed = hash_password("CorrectPassword")
    assert verify_password("WrongPassword", hashed) is False
