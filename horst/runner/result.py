class _Result:

    def __init__(self, output):
        self.output = output


class Ok(_Result):
    pass


class Error(_Result):
    pass


class UpToDate(_Result):
    pass


class Dry(_Result):
    pass