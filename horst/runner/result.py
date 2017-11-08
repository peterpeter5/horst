class _Result:

    def __init__(self, output, exit_code=0):
        self.exit_code = exit_code
        self.output = output


class Ok(_Result):
    pass


class Error(_Result):
    pass


class UpToDate(_Result):
    pass


class Dry(_Result):
    pass