class AppError(Exception):
    status_code = 400
    message = "Application error"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)
        self.message = message or self.message


class InvalidCredentialsError(AppError):
    status_code = 401
    message = "Invalid username or password"


class InvalidTokenError(AppError):
    status_code = 401
    message = "Invalid or expired token"


class NumberNotFoundError(AppError):
    status_code = 404
    message = "Number not found"


class ValidationError(AppError):
    status_code = 422
    message = "Invalid input"
