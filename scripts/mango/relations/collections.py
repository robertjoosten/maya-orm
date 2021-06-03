from mango.relations import base
from mango.relations.constants import CASCADE


__all__ = [
    "Collection",
]


class Collection(base.Relation):
    def __init__(
            self,
            cls=None,
            name=None,
            multi=True,
            hidden=False,
            persist=True,
            typed=False,
            validators=(),
            on_delete=CASCADE
    ):
        """
        Collections allow for a relation to be created on the source model
        only. The message attribute of the target is used to connect to the
        source attribute. This means that collection relations are always
        reverse relations.
        """
        super(Collection, self).__init__(
            cls=cls,
            name=name,
            rev_name="message",
            rev_hidden=True,
            rev_relation=None,
            hidden=hidden,
            persist=persist,
            typed=typed,
            on_delete=on_delete,
            validators=validators,
            multi=multi,
        )

        self.rev = True
