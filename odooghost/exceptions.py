class OdooGhostException(Exception):
    ...


class StreamOutputError(OdooGhostException):
    ...


class StreamParseError(OdooGhostException):
    ...


class ContextAlreadySetupError(OdooGhostException):
    ...


class StackException(OdooGhostException):
    ...


class StackImageBuildError(StackException):
    ...


class StackAlreadyExistsError(StackException):
    ...


class StackImageEnsureError(StackException):
    ...


class StackImagePullError(StackImageEnsureError):
    ...
