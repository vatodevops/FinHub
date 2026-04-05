class AppError(Exception):
    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, detail: str = "An unexpected error occurred"):
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail)


class ConflictError(AppError):
    status_code = 409
    error_code = "conflict"

    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(detail)


class ExternalServiceError(AppError):
    status_code = 502
    error_code = "external_service_error"

    def __init__(self, detail: str = "External service error"):
        super().__init__(detail)


class ValidationError(AppError):
    status_code = 422
    error_code = "validation_error"

    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail)
