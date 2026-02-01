import pytest
from datetime import timedelta
from jose import jwt
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.config import settings

# --- Password Hashing Tests ---

def test_hash_password():
    password = "secret_password"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > 10

def test_verify_password_correct():
    password = "secret_password"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True

def test_verify_password_incorrect():
    password = "secret_password"
    hashed = hash_password(password)
    assert verify_password("wrong_password", hashed) is False

# --- Token Tests ---

def test_create_access_token():
    data = {"user_id": "123"}
    token = create_access_token(data=data)
    
    # Manually decode to verify contents
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["user_id"] == "123"
    assert "exp" in decoded

def test_decode_access_token_success():
    data = {"user_id": "456"}
    token = create_access_token(data)
    payload = decode_access_token(token)
    assert payload["user_id"] == "456"

def test_decode_access_token_missing_user_id():
    # Create a token without user_id to trigger your custom error
    token = jwt.encode({"sub": "no_user_id"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    with pytest.raises(ValueError, match="invalid or expired token"):
        decode_access_token(token)

def test_decode_access_token_expired():
    # Create a token that expired 1 minute ago
    data = {"user_id": "789"}
    expires = timedelta(minutes=-1)
    token = create_access_token(data, expires_delta=expires)
    
    with pytest.raises(ValueError, match="invalid or expired token"):
        decode_access_token(token)

def test_decode_access_token_invalid_signature():
    token = create_access_token({"user_id": "123"})
    # Tamper with the token string
    invalid_token = token[:-5] + "aaaaa"
    
    with pytest.raises(ValueError, match="invalid or expired token"):
        decode_access_token(invalid_token)