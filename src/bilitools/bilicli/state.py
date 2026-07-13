"""Persistent login state helpers.

Phase 1 keeps the old ``requests.Session``-based API layer alive, but introduces a
stable credential representation compatible with ``bilibili-api-python``.
"""

from __future__ import annotations

from dataclasses import dataclass
from http.cookiejar import CookieJar
from typing import Any

import requests
from bilibili_api import Credential

_CREDENTIAL_KEYS = (
    "SESSDATA",
    "bili_jct",
    "buvid3",
    "buvid4",
    "DedeUserID",
    "ac_time_value",
)


@dataclass(slots=True, frozen=True)
class CredentialState:
    """Serializable credential fields used by both API backends."""

    sessdata: str | None = None
    bili_jct: str | None = None
    buvid3: str | None = None
    buvid4: str | None = None
    dedeuserid: str | None = None
    ac_time_value: str | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "CredentialState":
        """Build from a JSON-compatible mapping."""

        return cls(
            sessdata=data.get("SESSDATA") or data.get("sessdata"),
            bili_jct=data.get("bili_jct"),
            buvid3=data.get("buvid3") or data.get("BUVID3"),
            buvid4=data.get("buvid4") or data.get("BUVID4"),
            dedeuserid=data.get("DedeUserID") or data.get("dedeuserid"),
            ac_time_value=data.get("ac_time_value"),
        )

    @classmethod
    def from_cookiejar(cls, cookies: CookieJar) -> "CredentialState":
        """Build from a ``requests`` cookie jar."""

        return cls.from_mapping(requests.utils.dict_from_cookiejar(cookies))

    @classmethod
    def from_session(cls, session: requests.Session) -> "CredentialState":
        """Build from a legacy ``requests.Session``."""

        return cls.from_cookiejar(session.cookies)

    @classmethod
    def from_credential(cls, credential: Credential) -> "CredentialState":
        """Build from ``bilibili-api-python``'s credential object."""

        return cls(
            sessdata=credential.sessdata,
            bili_jct=credential.bili_jct,
            buvid3=credential.buvid3,
            buvid4=credential.buvid4,
            dedeuserid=credential.dedeuserid,
            ac_time_value=credential.ac_time_value,
        )

    def to_json(self) -> dict[str, str]:
        """Return a compact JSON-compatible mapping without empty fields."""

        data = {
            "SESSDATA": self.sessdata,
            "bili_jct": self.bili_jct,
            "buvid3": self.buvid3,
            "buvid4": self.buvid4,
            "DedeUserID": self.dedeuserid,
            "ac_time_value": self.ac_time_value,
        }
        return {key: value for key, value in data.items() if value}

    def to_cookie_dict(self) -> dict[str, str]:
        """Return cookies suitable for a legacy ``requests.Session``."""

        return self.to_json()

    def to_credential(self) -> Credential:
        """Return a ``bilibili-api-python`` credential object."""

        return Credential(
            sessdata=self.sessdata,
            bili_jct=self.bili_jct,
            buvid3=self.buvid3,
            buvid4=self.buvid4,
            dedeuserid=self.dedeuserid,
            ac_time_value=self.ac_time_value,
        )

    def apply_to_session(self, session: requests.Session) -> requests.Session:
        """Write credential cookies into a legacy session and return it."""

        session.cookies.update(self.to_cookie_dict())
        return session

    def is_empty(self) -> bool:
        """Whether no credential field is present."""

        return not any(self.to_json().values())


def credential_state_from_data(data: dict[str, Any]) -> CredentialState | None:
    """Extract credential state from a data file mapping if present."""

    raw = data.get("__credential")
    if isinstance(raw, dict):
        state = CredentialState.from_mapping(raw)
        return None if state.is_empty() else state

    legacy = {key: data.get(key) for key in _CREDENTIAL_KEYS if data.get(key)}
    if legacy:
        return CredentialState.from_mapping(legacy)
    return None
