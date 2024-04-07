from django.http import FileResponse
import os


class FileResponseWithCleanup(FileResponse):
    """
    A FileResponse that deletes the file on close.
    """
    def __init__(self, *args, **kwargs):
        self._file_path = kwargs.pop('file_path', None)
        super().__init__(*args, **kwargs)

    def close(self):
        super().close()
        if self._file_path:
            os.remove(self._file_path)