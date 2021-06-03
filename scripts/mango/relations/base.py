from mango import managers
from mango.relations.constants import CASCADE
from mango.utils import naming


__all__ = [
    "Relation",
]


class Relation(object):
    """
    The relationship class is the base descriptor that can be subclassed and
    used in the models. The descriptors have the possibility to link to other
    classes and it is possible to add a reverse link as well.
    """
    def __init__(
            self,
            cls,
            name=None,
            rev_name=None,
            rev_array=None,
            rev_hidden=None,
            rev_relation=None,
            hidden=False,
            persist=True,
            typed=False,
            on_delete=CASCADE,
            multi=False,
            validators=(),
    ):
        self.cls = cls
        self.name = name
        self.rev = False
        self.rev_name = rev_name
        self.rev_array = rev_array
        self.rev_hidden = rev_hidden if rev_hidden is not None else hidden
        self.rev_relation = rev_relation
        self.hidden = hidden
        self.persist = persist
        self.typed = typed
        self.on_delete = on_delete
        self.multi = multi
        self.validators = validators

    def __repr__(self):
        path = "{}.{}".format(self.__class__.__module__, self.__class__.__name__)
        name = getattr(self, "name", None)
        if name is not None:
            return "<{}: {}>".format(path, name)

        return "<{}>".format(path)

    # ------------------------------------------------------------------------

    def __get__(self, instance, owner=None):
        manager = self.get_manager_from_instance(instance)
        return manager if self.multi else manager.first()

    def __set__(self, instance, values):
        if not self.multi:
            values = values if isinstance(values, list) else [values]
            manager = self.get_manager_from_instance(instance)
            manager.set(*values)
        else:
            raise RuntimeError(
                "Cannot assign to a {0} object, "
                "use {0}.set() instead.".format(self.__class__.__name__)
            )

    def __delete__(self, instance):
        # get instance manager
        manager = self.get_manager_from_instance(instance)

        # delete child when cascading, it is possible to set this value to do
        # nothing, in which it will simply remove the relation.
        if not self.rev and self.on_delete == CASCADE:
            for obj in manager.all():
                obj.delete()

        # clear manager
        manager.clear()

    # ------------------------------------------------------------------------

    def add_manager_to_instance(self, instance):
        """
        Add a connection attribute to the instance. The connection attribute
        is a maya message attribute, depending on the multi and rev settings
        the connection will be hidden and is determined to only be a source
        or a destination. When a relation is set to be hidden the attribute
        is hidden. The attribute is controlled by a manager. This manager gets
        stored on the instance and will be returned.

        :param models.Model instance:
        :return: Manager
        :rtype: managers.Manager
        """
        # create manager
        manager = managers.Manager(
            instance,
            self.name,
            self.rev_name,
            rev=self.rev,
            cls=self.cls,
            typed=self.typed,
            validators=self.validators,
        )

        # add manager
        name = "_{}".format(self.name)
        setattr(instance, name, manager)

        # add attribute
        manager.add_attribute_to_instance(
            instance,
            multi=self.multi,
            hidden=self.hidden,
        )

        return manager

    # ------------------------------------------------------------------------

    def get_manager_from_instance(self, instance):
        """
        :param models.Model instance:
        :return: Manager
        :rtype: managers.Manager
        """
        name = "_{}".format(self.name)
        return getattr(instance, name)

    def generate_rev_name(self, name):
        """
        Generate a rev name based of the provided object and if its a multi
        object or not. If it is an s will be appended to the name if the name
        doesn't already end with an s.

        :param str name:
        :return: Rev name
        :rtype: str
        """
        rev_name = naming.upper_camel_to_snake_case(name)
        rev_name = rev_name if not self.rev_array else "{}_set".format(rev_name)
        return rev_name
