"""
Central custom exceptions. Raised by services/repositories, caught by
the global exception handlers registered in main.py.
"""


class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", details: dict | None = None):
        super().__init__(message, status_code=404, details=details)


class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed", details: dict | None = None):
        super().__init__(message, status_code=422, details=details)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication required", details: dict | None = None):
        super().__init__(message, status_code=401, details=details)


class ForbiddenError(AppException):
    def __init__(self, message: str = "You do not have permission to perform this action", details: dict | None = None):
        super().__init__(message, status_code=403, details=details)


class ConflictError(AppException):
    def __init__(self, message: str = "Resource conflict", details: dict | None = None):
        super().__init__(message, status_code=409, details=details)
