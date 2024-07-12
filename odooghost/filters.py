import enum

from odooghost.constant import LABEL_ONE_OFF
from odooghost.types import Labels


@enum.unique
class OneOffFilter(enum.Enum):
    include = 0
    exclude = 1
    only = 2

    @classmethod
    def update_labels(cls, value: "OneOffFilter", labels: Labels) -> None:
        if value == cls.only:
            labels.update({LABEL_ONE_OFF: "True"})
        elif value == cls.exclude:
            labels.update({LABEL_ONE_OFF: "False"})
        elif value == cls.include:
            pass
