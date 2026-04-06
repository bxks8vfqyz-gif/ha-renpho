"""Client for Renpho body girth (tape measure) measurements.

Uses the legacy renpho.qnclouds.com API, which requires RSA-encrypted
password auth and returns neck/shoulder/chest/waist/hip/etc. measurements.
"""
from __future__ import annotations

import base64
import logging

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding

_LOGGER = logging.getLogger(__name__)

_BASE_URL = "https://renpho.qnclouds.com/api/v3"
_APP_ID = "Renpho"
_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Renpho/2.1.0 (iPhone; iOS 14.4; Scale/2.1.0; en-US)",
    "Accept-Language": "en-US",
}
_PUBLIC_KEY_PEM = (
    b"-----BEGIN PUBLIC KEY-----\n"
    b"MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+25I2upukpfQ7rIaaTZtVE744\n"
    b"u2zV+HaagrUhDOTq8fMVf9yFQvEZh2/HKxFudUxP0dXUa8F6X4XmWumHdQnum3zm\n"
    b"Jr04fz2b2WCcN0ta/rbF2nYAnMVAk2OJVZAMudOiMWhcxV1nNJiKgTNNr13de0EQ\n"
    b"IiOL2CUBzu+HmIfUbQIDAQAB\n"
    b"-----END PUBLIC KEY-----"
)


class GirthClient:
    """Fetches the most recent body girth measurement from the Renpho legacy API."""

    def __init__(self, email: str, password: str) -> None:
        self._email = email
        self._password = password

    def _encrypt_password(self) -> str:
        public_key = serialization.load_pem_public_key(_PUBLIC_KEY_PEM)
        encrypted = public_key.encrypt(
            self._password.encode(),
            asym_padding.PKCS1v15(),
        )
        return base64.b64encode(encrypted).decode()

    def fetch(self) -> dict:
        """Login and return the most recent girth measurement dict, or {} if none."""
        token, user_id = self._login()
        return self._get_latest_girth(token, user_id)

    def _login(self) -> tuple[str, int]:
        resp = requests.post(
            f"{_BASE_URL}/users/sign_in.json",
            json={
                "secure_flag": "1",
                "email": self._email,
                "password": self._encrypt_password(),
            },
            headers=_HEADERS,
            params={"app_id": _APP_ID},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status_code") != "20000":
            raise ValueError(f"Renpho girth login failed: {data.get('status_message')}")
        return data["terminal_user_session_key"], data["id"]

    def _get_latest_girth(self, token: str, user_id: int) -> dict:
        resp = requests.get(
            f"{_BASE_URL}/girths/list_girth.json",
            headers=_HEADERS,
            params={
                "user_id": user_id,
                "last_updated_at": 883612800,
                "locale": "en",
                "app_id": _APP_ID,
                "terminal_user_session_key": token,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status_code") != "20000":
            raise ValueError(f"Renpho girth fetch failed: {data.get('status_message')}")
        girths = data.get("girths") or []
        if not girths:
            _LOGGER.debug("No girth measurements found")
            return {}
        return girths[-1]  # most recent
