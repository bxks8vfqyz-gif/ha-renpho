"""Girth client using the new cloud.renpho.com API.

Reuses the auth token from RenphoClient (renpho-api) to call
RenphoHealth/girth/queryAllGirthDataList — the same API your account
lives on, so Apple Sign-In accounts work here.
"""
from __future__ import annotations

import base64
import json
import logging

import requests
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

_LOGGER = logging.getLogger(__name__)

_BASE_URL = "https://cloud.renpho.com"
_AES_KEY = b"ed*wijdi$h6fe3ew"

_GIRTH_PATH = "/RenphoHealth/renpho/girth/queryAllGirthsDataList"


def _aes_encrypt(plaintext: str) -> str:
    padder = sym_padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode()) + padder.finalize()
    encryptor = Cipher(algorithms.AES(_AES_KEY), modes.ECB()).encryptor()
    return base64.b64encode(encryptor.update(padded) + encryptor.finalize()).decode()


def _aes_decrypt(b64_data: str) -> str:
    decryptor = Cipher(algorithms.AES(_AES_KEY), modes.ECB()).decryptor()
    padded = decryptor.update(base64.b64decode(b64_data)) + decryptor.finalize()
    unpadder = sym_padding.PKCS7(128).unpadder()
    return (unpadder.update(padded) + unpadder.finalize()).decode()


def _encrypt_body(obj: dict) -> dict:
    return {"encryptData": _aes_encrypt(json.dumps(obj, separators=(",", ":")))}


class CloudGirthClient:
    """Fetches girth measurements from cloud.renpho.com using an existing auth token."""

    def __init__(self, token: str, user_id: str | int) -> None:
        self._token = token
        self._user_id = str(user_id)

    @property
    def _headers(self) -> dict:
        return {
            "token": self._token,
            "userId": self._user_id,
            "appVersion": "6.6.0",
            "platform": "android",
        }

    def fetch_all(self) -> list[dict]:
        """Return all girth records, newest first. Returns [] if endpoint unavailable."""
        records: list[dict] = []
        page = 1
        while True:
            body = _encrypt_body({
                "pageNum": page,
                "pageSize": 100,
                "userIds": [self._user_id],
            })
            resp = requests.post(
                f"{_BASE_URL}{_GIRTH_PATH}",
                json=body,
                headers=self._headers,
                timeout=30,
            )
            resp.raise_for_status()
            result = resp.json()
            _LOGGER.debug("Cloud girth page %d raw response code=%s", page, result.get("code"))

            if not result.get("data"):
                if page == 1:
                    _LOGGER.warning(
                        "Cloud girth endpoint returned no data: code=%s msg=%s",
                        result.get("code"),
                        result.get("msg"),
                    )
                break

            payload = json.loads(_aes_decrypt(result["data"]))

            # API returns either a list directly or a dict wrapping a list
            if isinstance(payload, list):
                batch = payload
            elif isinstance(payload, dict):
                batch = (
                    payload.get("girthDataList")
                    or payload.get("measureDataList")
                    or payload.get("list")
                    or payload.get("data")
                    or []
                )
            else:
                batch = []

            if not batch:
                break

            records.extend(batch)

            total = payload.get("total", 0) if isinstance(payload, dict) else 0
            if len(batch) < 100 or (total and len(records) >= total):
                break
            page += 1

        return records

    def get_latest(self) -> dict:
        """Return the most recent girth record, or {} if none."""
        records = self.fetch_all()
        if not records:
            return {}
        # Sort by timestamp descending, return newest
        records.sort(key=lambda r: r.get("timeStamp") or r.get("time_stamp") or 0, reverse=True)
        return records[0]
