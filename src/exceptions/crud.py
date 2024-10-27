from .base import APIBaseException

class RepoNotFoundException(APIBaseException):
    def __init__(self, detail: str, status_code: int = 404):
        super().__init__(status_code=status_code, detail=detail)


class RepoConflictException(APIBaseException):
    def __init__(self, detail: str, status_code: int = 409):
        super().__init__(status_code=status_code, detail=detail)


class AlreadyExistsException(APIBaseException):
    def __init__(self, detail: str, status_code: int = 409):
        super().__init__(status_code=status_code, detail=detail)