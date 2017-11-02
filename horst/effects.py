from os import path


class EffectBase:

    def __repr__(self):

        return self.__class__.__name__

    def __eq__(self, other):
        return str(self.__repr__()) == str(other.__repr__())


class ErrorBase:
    def __init__(self, reason):
        self.reason = reason

    def __repr__(self):
        return "[Error] : [%s] : Reason: %s" % (self.__class__.__name__, self.reason)


class CreateFile(EffectBase):

    def __init__(self, file_path, content):
        self.file_path = file_path
        self.content = content

    def __repr__(self):
        return "[CreateFile] : <%s> : at <%s>" % list(reversed(path.split(self.file_path)))


class UpdateFile(EffectBase):

    def __init__(self, file_path, lineno_content):
        self.file_path = file_path
        self.line_and_content = lineno_content
    
    def __repr__(self):
        _, filename = path.split(self.file_path)
        return "[UpdateFile] : <%s> " % filename


class RunCommand(EffectBase):

    def __init__(self, command, arguments):
        self.command = command
        self.arguments = arguments

    def __repr__(self):
        return "[RunCommand] : <%s>" % self.command

    def __str__(self):
        return "%s %s" % (self.command, " ".join(map(str, self.arguments)))


class