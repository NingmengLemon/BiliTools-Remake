from typing import Optional

__all__ = ["BiliError"]

class BiliError(Exception):
    def __init__(self, code: int, message: Optional[str] = "unknown error"):
        self.code = code
        self.message = message
        super().__init__(f"Code {code}: {message}")
