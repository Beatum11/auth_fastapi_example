class UserNotFoundError(Exception):
    pass

class UserAlreadyVerifiedError(Exception):
    pass

class InvalidTokenError(Exception):
    pass

class InvalidCodeVerifierError(Exception):
    pass

class GoogleAPIError(Exception):
    pass