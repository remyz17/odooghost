import typing as t

import giturlparse

Filters = t.Dict[str, str]
Labels = Filters
Attrs = t.Dict[str, t.Any]
AddonsType = t.Literal["remote", "local"]


class GitOrigin:
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _):
        if not isinstance(v, str):
            raise TypeError("string required")

        parsed = giturlparse.parse(v)
        if not parsed.valid:
            raise ValueError("invalid git url")

        # Retourner l'objet giturlparse plutôt que la chaîne
        return parsed
