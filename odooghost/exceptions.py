class OdooGhostException(Exception):
    ...


class StreamOutputError(OdooGhostException):
    ...


class StreamParseError(OdooGhostException):
    ...


class ContextAlreadySetupError(OdooGhostException):
    ...


class CommonNetworkEnsureError(OdooGhostException):
    ...


class StackException(OdooGhostException):
    ...


class StackConfigError(StackException):
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


class AddonsError(StackException):
    ...


class InvalidAddonsPathError(AddonsError):
    ...


class AddonsGitError(AddonsError):
    ...


class AddonsGitCloneError(AddonsGitError):
    ...
