import abc
from maya.api import OpenMaya

from mango.utils import api


__all__ = [
    "Field",
]


class Field(object):
    """
    The field class is the base descriptor that can be subclassed and used
    in the models. The descriptors have the possibility to validate provided
    values. It is possible for fields to persist through subclasses if the
    persist flag is set.
    """
    mfn = None
    mfn_type = None
    array = False
    compound = None
    default_value = None

    def __init__(
            self,
            name=None,
            editable=True,
            persist=True,
            choices=None,
            min_value=None,
            max_value=None,
            default_value=None,
            default_value_only=False,
            hidden=False,
            keyable=False,
            channel_box=False,
    ):
        # set keyword arguments
        self.name = name
        self.editable = editable if not default_value_only else False
        self.persist = persist
        self.choices = choices
        self.min_value = min_value
        self.max_value = max_value
        self.default_value = default_value or self.default_value
        self.default_value_only = default_value_only
        self.hidden = hidden
        self.keyable = keyable
        self.channel_box = channel_box

        # set default validators
        self._validators = []

        if not self.editable:
            self._validators.append(self.validate_editable)
        if self.default_value_only:
            self._validators.append(self.validate_default_only)
        if self.min_value is not None:
            self._validators.append(self.validate_min_value)
        if self.max_value is not None:
            self._validators.append(self.validate_max_value)
        if self.array or self.compound:
            self._validators.append(self.validate_list_or_tuple)

    def __repr__(self):
        path = "{}.{}".format(self.__class__.__module__, self.__class__.__name__)
        name = getattr(self, "name", None)
        if name is not None:
            return "<{}: {}>".format(path, name)

        return "<{}>".format(path)

    def __get__(self, instance, owner=None):
        return self.get(instance)

    def __set__(self, instance, value):
        self.set(instance, value, initialize=False)

    # ------------------------------------------------------------------------

    def get(self, instance):
        """
        :param models.Model instance:
        :return: Value
        :rtype: str/int/float/list/tuple/dict/None
        """
        def process_plug(plug_):
            """
            Utility function to retrieve a plug value. It is a function
            that will call on itself until the arrays and compounds are
            resolved and eventually the get_plug_value can be called.

            :param OpenMaya.OpenMaya plug_:
            :return: Value
            """
            if plug_.isArray:
                # loop over all elements and re-call the function using the
                # local element index plug.
                return [
                    process_plug(plug_.elementByLogicalIndex(i))
                    for i in range(plug_.evaluateNumElements())
                ]

            elif plug_.isCompound:
                # loop over all children and re-call the function using the
                # child plug.
                return tuple(
                    process_plug(plug_.child(i))
                    for i in range(plug_.numChildren())
                )

            else:
                value = self.get_plug_value(plug_)
                return value

        plug = instance.get_plug(self.name)
        return process_plug(plug)

    def set(self, instance, value, initialize=False):
        """
        :param models.Model instance:
        :param str/int/float/list/tuple/dict/None value:
        :param bool initialize:
        """
        def process_plug(plug_, value_):
            """
            Utility function to set a plug value. It is a function that will
            call on itself until the arrays and compounds are resolved and
            eventually the set_plug_value can be called.

            :param OpenMaya.MPlug plug_:
            :param str/int/float/bool/list/tuple/None value_:
            """
            if plug_.isArray:
                # loop over all elements and re-call the function using the
                # local element index plug.
                for i, value_element in enumerate(value_):
                    plug_element = plug_.elementByLogicalIndex(i)
                    plug_element = self.get_parent_plug(plug_element)
                    process_plug(plug_element, value_element)

                # remove any excess elements
                for i in range(len(value_), plug_.evaluateNumElements()):
                    plug_element = plug.elementByLogicalIndex(i)
                    modifier.removeMultiInstance(plug_element, True)

            elif plug_.isCompound:
                # loop over all children and re-call the function using the
                # child plug.
                for i, value_child in enumerate(value_):
                    plug_child = plug_.child(i)
                    plug_child = self.get_parent_plug(plug_child)
                    process_plug(plug_child, value_child)

            else:
                return self.set_plug_value(modifier, plug_, value_)

        # run validators
        for validator in self.validators[bool(initialize):]:
            validator(value)

        # get plug
        plug = instance.get_plug(self.name)
        plug = self.get_parent_plug(plug)

        # create modifier
        with api.MDGModifier() as modifier:
            process_plug(plug, value)

    # ------------------------------------------------------------------------

    @abc.abstractmethod
    def get_plug_value(self, plug):
        """
        :param OpenMaya.MPlug plug:
        :return: Value
        :rtype: str/int/float/bool/list/tuple/None
        """
        pass

    @abc.abstractmethod
    def set_plug_value(self, modifier, plug, value):
        """
        :param OpenMaya.MDGModifier modifier:
        :param OpenMaya.MPlug plug:
        :param str/int/float/bool/list/tuple/None value:
        """
        pass

    # ------------------------------------------------------------------------

    def default(self, index=None):
        """
        Get the default value based on an index. By default this function
        handles four states. When a field is a compound field and the index
        is None ( meaning the parent attribute ) no default value can be
        present, the same goes for array attributes. Then based on the index
        either the entire default value or the provided index of the default
        value will be returned.

        :param int/None index:
        :return: Default value
        """
        if (self.compound and index is None) or self.array:
            return None
        elif index is not None:
            return self.default_value[index]
        else:
            return self.default_value

    def create(self):
        """
        Create the attribute using the state of the class. This function
        handles the creation or any attribute but contains special handling
        to deal with compound attributes.

        :return: Attribute
        :rtype: OpenMaya.MObject
        """
        # get types
        mfn = self.mfn if not self.compound else OpenMaya.MFnCompoundAttribute()
        mfn_type = self.mfn_type if not self.compound else None

        # get creation arguments
        args = [self.name, self.name]
        default = self.default()

        if mfn_type is not None:
            args.append(mfn_type)

        # create attribute
        attribute = mfn.create(*args)
        mfn.hidden = self.hidden
        mfn.keyable = self.keyable
        mfn.channelBox = self.channel_box
        mfn.array = self.array

        if default is not None:
            mfn.default = default

        # create children attributes
        for index, axis in enumerate(self.compound or []):
            child_name = self.name + axis
            child_attribute = self.mfn.create(child_name, child_name, self.mfn_type)

            child_default = self.default(index)
            if child_default is not None:
                self.mfn.default = child_default

            self.mfn.hidden = self.hidden
            self.mfn.keyable = self.keyable
            self.mfn.channelBox = self.channel_box
            mfn.addChild(child_attribute)

        return attribute

    # ------------------------------------------------------------------------

    def add_attribute_to_instance(self, instance):
        """
        Create the field attribute to the instance. This function will take
        the fields settings into account. It is possible to create arrays,
        compounds and all sorts of other attribute types.

        :param models.Model instance:
        """
        # validate name
        if instance.has_attribute(self.name):
            return

        # add attribute
        attribute = self.create()
        instance.add_attribute(attribute)

    def get_parent_plug(self, plug):
        """
        It is possible for fields to get connected via a proxy attribute
        connection. This function will find that connection and return it
        as a plug so the attribute can safely be set.

        :param  OpenMaya.MPlug plug:
        :return: Parent plug
        :rtype: OpenMaya.MPlug
        """
        return plug.source() if plug.isDestination else plug

    # ------------------------------------------------------------------------

    @property
    def validators(self):
        """
        :return: Validators
        :rtype: list
        """
        return self._validators

    # ------------------------------------------------------------------------

    def validate_editable(self, value):
        """
        :raise RuntimeError: When the field is not editable.
        """
        # validate if the field is editable
        if not self.editable:
            raise RuntimeError("{} '{}' is not editable.".format(self.__class__.__name__, self.name))

    def validate_default_only(self, value):
        """
        :raise RuntimeError:
            When the field is only allowed to take in the default value.
        """
        # validate if the field is default value only
        if self.default_value_only and value != self.default_value:
            raise RuntimeError(
                "{} '{}' only allows for the default value '{}' to be set.".format(
                    self.__class__.__name__,
                    self.name,
                    self.default_value
                )
            )

    def validate_min_value(self, value):
        """
        :raise ValueError:
            When the value is not bigger than the provided min value.
        """
        if self.min_value is not None and self.min_value > value:
            raise ValueError(
                "{} value '{}' is smaller than minimum value '{}'".format(
                    self.__class__.__name__,
                    value,
                    self.min_value
                )
            )

    def validate_max_value(self, value):
        """
        :raise ValueError:
            When the value is not smaller than the provided max value.
        """
        if self.max_value is not None and self.max_value < value:
            raise ValueError(
                "{} value '{}' is bigger than maximum value '{}'".format(
                    self.__class__.__name__,
                    value,
                    self.max_value
                )
            )

    def validate_list_or_tuple(self, value):
        """
        :raise TypeError: When the value is not a list.
        """
        if not isinstance(value, (list, tuple)):
            raise TypeError(
                "{} requires a 'list/tuple' value, '{}' provided.".format(
                    self.__class__.__name__,
                    type(value).__name__
                )
            )