from os import path


class DryRun:

    def __init__(self, effect):
        self._effect = effect

    def __str__(self):
        return self._effect.__str__()

    def __repr__(self):
        return self._effect.__repr__()

    def __display__(self):
        return self._effect.__display__()


class EffectBase:
    verbose = True

    def __repr__(self):
        return self.__class__.__name__

    def __eq__(self, other):
        return str(self.__repr__()) == str(other.__repr__())

    def __display__(self):
        return self.__repr__()

    def __format__(self, format_spec):
        return repr(self)


class ErrorBase:
    def __init__(self, reason):
        self.reason = reason

    def __repr__(self):
        return "[Error] : [%s] : Reason: %s" % (self.__class__.__name__, self.reason)

    def __format__(self, format_spec):
        return repr(self)


class StageConfigError(ErrorBase):
    pass


class DeleteFileOrFolder(EffectBase):

    def __init__(self, abspath):
        self.file_of_folder = abspath

    def __format__(self, format_spec):
        _, name = path.split(self.file_of_folder)
        return "[delete file/folder: %s]" % name


class _FileOp(EffectBase):
    def __init__(self, file_path, content):
        self.file_path = file_path
        self.content = content


class CopyTree(_FileOp):
    pass

    def __format__(self, format_spec):
        return "[copy-tree: %s]" % self.file_path


class CreateFile(_FileOp):

    def __repr__(self):
        return "[CreateFile] : <%s> : at <%s>" % tuple(reversed(path.split(self.file_path)))

    def __format__(self, format_spec):
        _, name = path.split(self.file_path)
        return "[create file: %s]" % name


class UpdateFile(_FileOp):

    def __repr__(self):
        _, filename = path.split(self.file_path)
        return "[UpdateFile] : <%s> " % filename

    def __format__(self, format_spec):
        _, name = path.split(self.file_path)
        return "[update file: %s]" % name


class RunCommand(EffectBase):

    def __init__(self, command, arguments):
        self.command = command
        self.arguments = arguments

    def __repr__(self):
        return "[RunCommand] : <%s>" % str(self)

    def __str__(self):
        return "%s %s" % (self.command, " ".join(map(str, self.arguments)))


class RunOption:

    def __init__(self, name, value=None, hyphens=None):
        self.name = name
        self.value = value
        self.hyphens = min(len(name), 2) if hyphens is None else hyphens

    def __str__(self):
        return "-" * self.hyphens + \
               ('%s="%s"' % (self.name, str(self.value)) if self.value is not None else self.name)

    def __eq__(self, other):
        return str(self) == str(other)

    def __repr__(self):
        return str(self)


class Printer(EffectBase):
    def __init__(self, message):
        self.message = message
