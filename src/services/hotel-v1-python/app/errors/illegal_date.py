class IllegalDateException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.errors = "Illegal Date Exception"
        print(self.errors)
