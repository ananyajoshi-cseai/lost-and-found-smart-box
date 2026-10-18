import os
import secrets
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

basic = HTTPBasic(auto_error=False)


def validate_configuration():
    for name in ("DEVICE_KEY", "STAFF_USERNAME", "STAFF_PASSWORD"):
        if not os.getenv(name):
            raise RuntimeError(f"Set {name} before starting the server")


def require_device(x_device_key: str | None = Header(default=None)):
    expected = os.getenv("DEVICE_KEY", "")
    if not expected or x_device_key is None or not secrets.compare_digest(x_device_key.encode(), expected.encode()):
        raise HTTPException(401, "Invalid device credential")


def require_staff(credentials: HTTPBasicCredentials | None = Depends(basic)):
    username, password = os.getenv("STAFF_USERNAME", ""), os.getenv("STAFF_PASSWORD", "")
    if credentials is None or not username or not password:
        raise HTTPException(401, "Staff authentication required", headers={"WWW-Authenticate": "Basic"})
    user_ok = secrets.compare_digest(credentials.username.encode(), username.encode())
    pass_ok = secrets.compare_digest(credentials.password.encode(), password.encode())
    if not (user_ok and pass_ok):
        raise HTTPException(401, "Invalid staff credential", headers={"WWW-Authenticate": "Basic"})
    return credentials.username
