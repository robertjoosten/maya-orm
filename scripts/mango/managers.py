import six
import abc
import logging
import operator
from maya.api import OpenMaya

from mango.utils import api


log = logging.getLogger("mango")


@six.add_metaclass(abc.ABCMeta)
class ManagerBase(object):
    """
    The manager class can be used to manage a set of models. It will be
    possible to add and more objects from the list and filter using keys
    and values. It is possible to manage only direct instances of a cls
    or using any of its subclasses.
    """
    def __init__(self, cls, typed=True, validators=()):
        self.cls = cls
        self.typed = typed

        self._validators = []

        if typed:
            self._validators.append(self.validate_obj_is_subclass)
        else:
            self._validators.append(self.validate_obj_is_instance)

        self._validators.extend(validators)

    def __repr__(self):
        return "<{}.{}>".format(
            self.__class__.__module__,
            self.__class__.__name__,
        )

    def __getitem__(self, item):
        """
        :param int item:
        :raise TypeError: When item is not an integer.
        :raise Index: When item is out of range.
        """
        return self.all()[item]

    # ------------------------------------------------------------------------

    def create(self, **kwargs):
        """
        Create and add an instance of the cls model using the provided keyword
        arguments. It is possible to override the class by added in cls
        keyword argument if you are with a typed manager. This cls will be
        part of the validation process to ensure that actually is matching the
        typed manager.

        :param kwargs:
        :return: Instance
        :rtype: models.Model
        """
        cls = kwargs.pop("cls", self.cls)
        instance = cls(**kwargs)
        return instance

    # ------------------------------------------------------------------------

    def first(self):
        """
        :return: First instance of the models list
        :rtype: models.Model/None
        """
        return next(self.all_iter(), None)

    def get(self, **kwargs):
        """
        :return: First instance of a match in the model list
        :rtype: models.Model/None
        """
        return next(self.filter_iter(**kwargs), None)

    def get_or_create(self, **kwargs):
        """
        Return the an existing model matching the keyword arguments. If it
        doesn't the keyword arguments will be used to create the model.

        :return: Model
        :rtype: models.Model
        """
        get_kwargs = kwargs.copy()
        get_kwargs.pop("cls", None)

        model = self.get(**get_kwargs)
        if model is None:
            model = self.create(**kwargs)

        return model

    # ------------------------------------------------------------------------

    def filter_iter(self, **kwargs):
        """
        :return: Filtered models
        :rtype: generator[models.Model]
        :raise RuntimeError: When the provided operator cannot be found.
        """
        # convert kwargs into actual keys and the validation function. The
        # filter supports keys with double underscores like name__contains,
        # index__lt etc. These are split to retrieve the key and the
        # function. If no function is found we assume eq.
        mapper = []
        for key, value in kwargs.items():
            if key.count("__"):
                # get operator
                key, func_name = key.split("__", 1)
                func = getattr(operator, func_name)

                # validate operator
                if func is None:
                    raise RuntimeError("Operator '{}' cannot be found "
                                       "in the operator package.".format(func_name))

                mapper.append((key, value, func))
            else:
                mapper.append((key, value, operator.eq))

        # filter objects
        for obj in self.all_iter():
            if all([func(getattr(obj, key, None), value) for key, value, func in mapper]):
                yield obj

    def filter(self, **kwargs):
        """
        The filter allows for operators to be attached to the keys. For
        example 'name_contains' or 'index_ge' it'll require getting used to
        the name of the rich operators. The operators package is used to do
        these comparisons.

        Cheat sheet:
            lt: a < b
            le: a <= b
            eq: a == b
            ne: a != b
            gt: a > b
            ge: a >= b

        :return: Filtered models
        :rtype: list[models.Model]
        :raise RuntimeError: When the provided operator cannot be found.
        """
        return list(self.filter_iter(**kwargs))

    # ------------------------------------------------------------------------

    @abc.abstractmethod
    def all_iter(self):
        """
        Abstract method that needs to be implemented to make sure that all
        models are found that belong to the manager.

        :return: Models
        :rtype: generator[models.Model]
        """
        pass

    def all(self):
        """
        :return: All models
        :rtype: list[models.Model]
        """
        return list(self.all_iter())

    def length(self):
        """
        :return: Length
        :rtype: int
        """
        return len(self.all())

    # ------------------------------------------------------------------------

    def validate_obj_is_instance(self, obj):
        """
        :param model.Model obj:
        :raise TypeError: When the provided model is not an instance of the class.
        """
        if obj and obj.__class__ != self.cls:
            raise TypeError(
                "'{}' object is not an instance of '{}'.".format(
                    obj.__class__.__name__,
                    self.cls.__name__
                )
            )

    def validate_obj_is_subclass(self, obj):
        """
        :param model.Model obj:
        :raise TypeError: When the provided model is not a subclass of the class.
        """
        if obj and not isinstance(obj, self.cls):
            raise TypeError(
                "'{}' object is not a subclass of '{}'.".format(
                    obj.__class__.__name__,
                    self.cls.__name__
                )
            )


class ManagerDefault(ManagerBase):
    """
    The default manager is used by the types themselves. It will help manage
    the instances that belong to the type. It will not only manage any of the
    instances of the type but also any instances that have inherited from the
    type.
    """
    def __init__(self, cls, typed=True, validators=()):
        super(ManagerDefault, self).__init__(cls, typed=typed, validators=validators)

    # ------------------------------------------------------------------------

    def all_iter(self):
        """
        :return: All models
        :rtype: generator[models.Model]
        """
        if self.typed:
            for name in getattr(self.cls, "_types_future")[self.cls.__name__]:
                for obj in six.itervalues(getattr(self.cls, "_instances_typed")[name]):
                    yield obj
        else:
            for obj in six.itervalues(getattr(self.cls, "_instances_typed")[self.cls.__name__]):
                yield obj


class Manager(ManagerBase):
    """
    The manager class can be used to manage a set of models. It will be
    possible to add and more objects from the list and filter using keys
    and values. It is possible to manage only direct instances of a cls
    or using any of its subclasses.
    """
    def __init__(self, instance, name, rev_name, rev=False, cls=None, typed=True, validators=()):
        cls = cls if cls else instance.__class__
        super(Manager, self).__init__(cls, typed=typed, validators=validators)

        self.instance = instance
        self.name = name
        self.rev_name = rev_name
        self.rev = rev

        if name == rev_name:
            raise RuntimeError(
                "Unable to create relation for '{}.{}', reverse name is not "
                "allowed to match.".format(
                    self.instance.name,
                    self.name
                )
            )

    def __repr__(self):
        return "<{}.{}: {}.{}>".format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.instance.name,
            self.name
        )

    # ------------------------------------------------------------------------

    def create(self, **kwargs):
        """
        Create and add an instance of the cls model using the provided keyword
        arguments. It is possible to override the class by added in cls
        keyword argument if you are with a typed manager. This cls will be
        part of the validation process to ensure that actually is matching the
        typed manager.

        :param kwargs:
        :return: Instance
        :rtype: models.Model
        """
        instance = super(Manager, self).create(**kwargs)
        self.add(instance)

        return instance

    def add(self, *models):
        """
        Loop over the provided models and add them to models list if they
        pass the validator checks.

        :param models.Model models:
        :return: Added models
        :rtype: tuple[models.Model]
        """
        def get_plug_element(plug_):
            """
            :param OpenMaya.MPlug plug_:
            :return: Plug path
            :rtype: str
            """
            if plug_.isArray:
                indices = plug_.getExistingArrayAttributeIndices()
                indices.append(-1)
                return plug_.elementByLogicalIndex(max(indices) + 1)

            return plug_

        # validate nodes
        if not models:
            return

        # variables
        models_added = []
        models_connected = self.all()

        # add nodes
        for model in models:
            # validate node
            if not model:
                continue
            elif isinstance(model, six.string_types):
                model = self.cls(model)

            if model == self.instance:
                log.warning("Node '{}' cannot be connected to itself.".format(self.instance.name))
                continue
            elif model in models_connected:
                log.warning("Node '{}' is already connected.".format(model.name))
                continue

            # run validators
            for validator in self._validators:
                validator(model)

            # connections
            connections = [None, None]

            # get plugs
            plug = self.instance.get_plug(self.name)
            plug = get_plug_element(plug)
            connections[int(self.rev)] = plug

            plug = model.get_plug(self.rev_name)
            plug = get_plug_element(plug)
            connections[int(not self.rev)] = plug

            # connect plugs
            with api.MDGModifier() as modifier:
                modifier.connect(*connections)

            models_added.append(model)

        return tuple(models_added)

    def set(self, *models):
        """
        Loop over the provided models and add them to models list if they
        pass the validator checks. Before this happens the original list is
        cleared.

        :param tuple[models.Model] models:
        :return: Set models
        :rtype: tuple[models.Model]
        """
        self.clear()
        self.add(*models)

    def remove(self, *models, **options):
        """
        Loop over the provided models and remove them from the models list if
        they are part of the list.

        :param models.Model models:
        """
        # variables
        remove_all = options.get("remove_all", False)

        # validate
        if not remove_all and not models:
            return

        # get plugs
        plug = self.instance.get_plug(self.name)

        with api.MDGModifier() as modifier:
            # delete connections
            if plug.isArray:
                for index in plug.getExistingArrayAttributeIndices():
                    plug_element = plug.elementByLogicalIndex(index)
                    for plug_connected in plug_element.connectedTo(self.rev, not self.rev):
                        if remove_all or plug_connected.node() in models:
                            if plug.isElement:
                                modifier.removeMultiInstance(plug_connected, True)

                    modifier.removeMultiInstance(plug_element, True)
            else:
                for plug_connected in plug.connectedTo(self.rev, not self.rev):
                    if remove_all or plug_connected.node() in models:
                        if plug.isElement:
                            modifier.removeMultiInstance(plug_connected, True)
                        else:
                            connections = [None, None]
                            connections[int(self.rev)] = plug
                            connections[int(not self.rev)] = plug_connected
                            modifier.disconnect(*connections)

    def clear(self):
        """
        Remove all models from the manager.
        """
        self.remove(remove_all=True)

    # ------------------------------------------------------------------------

    def all_iter(self):
        """
        :return: Models
        :rtype: generator[models.Model]
        """
        plug = self.instance.get_plug(self.name)

        if plug.isArray:
            for index in plug.getExistingArrayAttributeIndices():
                plug_element = plug.elementByLogicalIndex(index)
                for plug_connected in plug_element.connectedTo(self.rev, not self.rev):
                    yield self.cls(plug_connected.node())
        else:
            for plug_connected in plug.connectedTo(self.rev, not self.rev):
                yield self.cls(plug_connected.node())

    # ------------------------------------------------------------------------

    def add_attribute_to_instance(self, instance, **kwargs):
        """
        Add a connection attribute to the instance. The connection attribute
        is a maya message attribute, depending on the multi and hidden
        settings the connection will be hidden and is determined to only be a source
        or a destination. When a relation is set to be hidden the attribute
        is hidden. The attribute is controlled by a manager. This manager gets
        stored on the instance and will be returned. It is possible to specify
        if the attribute to be added is the source or destination attribute.

        :param models.Model instance:
        """
        # get variables
        rev_input = kwargs.get("rev", False)
        rev = self.rev if not rev_input else not self.rev
        name = self.name if not rev_input else self.rev_name

        # validate name
        if instance.has_attribute(name):
            return

        # create attribute
        attribute_type = OpenMaya.MFnMessageAttribute()
        attribute = attribute_type.create(name, name)
        attribute_type.connectable = True
        attribute_type.array = kwargs.get("multi", False)
        attribute_type.writable = rev
        attribute_type.readable = not rev
        attribute_type.indexMatters = False
        attribute_type.hidden = kwargs.get("hidden", False)

        # add attribute
        instance.add_attribute(attribute)
