class OdooGhostException(Exception):
    ...


class ContextAlreadySetupError(OdooGhostException):
    ...


class StackException(OdooGhostException):
    ...


class StackAlreadyExistsError(StackException):
    ....

class StackImageEnsureError(StackException):
    ...


class StackImagePullError(StackImageEnsureError):
    ...
