from mango.relations import base
from mango.relations.constants import CASCADE


__all__ = [
    "OneToOneRel",
    "OneToManyRel",
    "ManyToOneRel",
    "ManyToManyRel",
]


class OneToOneRel(base.Relation):
    def __init__(
            self,
            cls=None,
            name=None,
            rev_name=None,
            rev_hidden=None,
            hidden=False,
            persist=True,
            typed=False,
            validators=(),
            on_delete=CASCADE
    ):
        super(OneToOneRel, self).__init__(
            cls=cls,
            name=name,
            rev_name=rev_name,
            rev_hidden=rev_hidden,
            rev_relation=OneToOneRel,
            hidden=hidden,
            persist=persist,
            typed=typed,
            on_delete=on_delete,
            validators=validators,
            multi=False,
        )


class OneToManyRel(base.Relation):
    def __init__(
            self,
            cls=None,
            name=None,
            rev_name=None,
            rev_hidden=None,
            hidden=False,
            persist=True,
            typed=False,
            validators=(),
            on_delete=CASCADE
    ):
        super(OneToManyRel, self).__init__(
            cls=cls,
            name=name,
            rev_name=rev_name,
            rev_hidden=rev_hidden,
            rev_relation=OneToOneRel,
            hidden=hidden,
            persist=persist,
            typed=typed,
            on_delete=on_delete,
            validators=validators,
            multi=True,
        )


class ManyToOneRel(base.Relation):
    def __init__(
            self,
            cls=None,
            name=None,
            rev_name=None,
            rev_hidden=None,
            hidden=False,
            persist=True,
            typed=False,
            validators=(),
            on_delete=CASCADE
    ):
        super(ManyToOneRel, self).__init__(
            cls=cls,
            name=name,
            rev_name=rev_name,
            rev_hidden=rev_hidden,
            rev_relation=OneToManyRel,
            hidden=hidden,
            persist=persist,
            typed=typed,
            on_delete=on_delete,
            validators=validators,
            multi=False,
        )


class ManyToManyRel(base.Relation):
    def __init__(
            self,
            cls=None,
            name=None,
            rev_name=None,
            rev_hidden=None,
            hidden=False,
            persist=True,
            typed=False,
            validators=(),
            on_delete=CASCADE
    ):
        super(ManyToManyRel, self).__init__(
            cls=cls,
            name=name,
            rev_name=rev_name,
            rev_hidden=rev_hidden,
            rev_relation=ManyToManyRel,
            hidden=hidden,
            persist=persist,
            typed=typed,
            on_delete=on_delete,
            validators=validators,
            multi=True,
        )