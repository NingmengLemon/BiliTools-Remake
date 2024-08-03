from typing import Any, Literal
from biliapis.template import APITemplate

class AudioAPIs(APITemplate):
    def get_info(self, auid: int) -> dict[str, Any]: ...
    def get_stream(
        self, auid: int, quality: Literal[0, 1, 2, 3] = 3
    ) -> dict[str, Any]: ...
    def get_tags(
        self, auid: int
    ) -> list[dict[Literal["type", "subtype", "key", "info"], str | int]]: ...
    def get_playmenu(
        self, amid: int, page: int = 1, page_size: int = 100
    ) -> dict[str, Any]: ...
