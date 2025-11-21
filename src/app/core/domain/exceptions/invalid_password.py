from http import HTTPStatus


class InvalidPasswordException(Exception):
    """Exception raised for invalid passwords."""
    http_status: int = HTTPStatus.BAD_REQUEST
    action: str = "Please ensure that your password meets the required criteria."

    def __init__(self, message: str = "The provided password is invalid."):
        self.message = message
        super().__init__(self.message)