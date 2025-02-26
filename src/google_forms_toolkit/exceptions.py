class GoogleFormsException(Exception):
    pass


class ParsingException(GoogleFormsException):
    pass


class ElementNotFoundException(ParsingException):
    pass
