USERNAME_IN_USE = 'username in use'
INVALID_TOKEN = 'invalid token'
AUCTION_NOT_FOUND = 'auction not found'
USER_NOT_ADMIN = 'user is not admin'
USER_NOT_FOUND = 'user was not found'
WRONG_CREDENTIALS = 'invalid username or password'
TOKEN_EXPIRED = 'token has expired'
USER_NOT_VALIDATED = 'user is not validated'
USER_NOT_AUTHORISED = 'user is not authorised'
AUCTION_ALREADY_STARTED = 'auction cannot be modified'
AUCTION_ALREADY_ENDED = 'auction has already ended'
AUCTION_HASNT_STARTED = 'auction has not started'
MESSAGE_NOT_FOUND = 'message was not found'


def camel_case(s):
    return s[0].lower() + s[1:]


class JsonException(Exception):
    def __init__(self, message='', data={}, details='', name='', code=500):
        self.message = message
        self.details = details
        self.data = data
        if not hasattr(self, 'code'):
            self.code = code
        self.name = name or camel_case(self.__class__.__name__)
        Exception.__init__(self, message, details, self.name, self.code)
