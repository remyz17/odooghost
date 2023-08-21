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


class CommonNetworkEnsureError(Exception):
    ...


class StackImageBuildError(StackException):
    ...


class StackAlreadyExistsError(StackException):
    ...


class StackNotFoundError(StackException):
    ...


class StackImageEnsureError(StackException):
    ...


class StackImagePullError(StackImageEnsureError):
    ...


class StackVolumeCreateError(StackException):
    ...


class StackContainerCreateError(StackException):
    ...


class StackContainerGetError(StackException):
    ...


class StackContainerNotFound(StackException):
    ...


class StackContainerStartError(StackException):
    ...
