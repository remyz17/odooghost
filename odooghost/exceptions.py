class OdooGhostException(Exception):
    ...


class ContextAlreadySetupError(OdooGhostException):
    ...


class StackException(OdooGhostException):
    ...


class StackImageEnsureError(StackException):
    ...


class StackImagePullError(StackImageEnsureError):
    ...
