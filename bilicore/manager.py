from biliapis import APIContainer

class DownloadManager:
    def __init__(self, apis: APIContainer) -> None:
        self._apis = apis

    def add_task(self):
        return NotImplemented
