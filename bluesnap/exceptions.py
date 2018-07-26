import re
import json

class APIError(Exception):
    """
    If description is passed, messages would be ignored
    """
    def __init__(self, messages=None, description=None, code=None, status_code=None):
        self.messages = messages
        self.description = str(description)
        self.code = code
        self.status_code = status_code

    def __str__(self):
        if self.description not in (None, 'None'):
            string = self.description
        else:
            if isinstance(self.messages, str):
                string = self.messages
            if isinstance(self.messages, list):
                string = json.dumps(self.messages, indent=2)

        if self.code is not None:
            string += ' (BlueSnap error code was {0})'.format(self.code)

        if self.status_code is not None:
            string += ' (HTTP status code was {status_code})'.format(status_code=self.status_code)

        return string


class CardError(Exception):
    simple_description_matcher = re.compile(
        'Order creation could not be completed because of payment processing failure: (\w+) - (.*)')

    def __init__(self, description, code=None, status_code=None):
        self.verbose_description = description
        self.code = str(code)
        self.status_code = str(status_code)

        # Extract simple description
        try:
            self.code = '{}-{}'.format(self.simple_description_matcher.match(self.verbose_description).group(1),
                                       self.code)
            self.description = self.simple_description_matcher.match(self.verbose_description).group(2)
        except (AttributeError, IndexError):
            self.description = self.verbose_description

    def __str__(self):
        string = self.description

        codes = filter(None, (self.code, self.status_code))
        if codes:
            string += ' (Error code was {})'.format('-'.join(codes))

        return string


class ImproperlyConfigured(Exception):
    pass


class ValidationError(Exception):
    pass
