class UnsolvableError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class TooManyUnknownsError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class NegativeOrZeroValueError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class NotANumberError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class DividedBeamError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class IncorrectInputError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class NonExistentError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class NoBeamError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class NoSupportsError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)