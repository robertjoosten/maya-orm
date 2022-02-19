import six
from maya.api import OpenMaya
from collections import OrderedDict

from mango.fields import base
from mango.fields import mixin
from mango.utils import decorator


__all__ = [
    "IntegerField",
    "EnumField",
    "FloatField",
    "DegreeField",
    "BooleanField",
    "StringField",
    "MatrixField",
]


class IntegerField(base.Field, mixin.MinMaxValidatorMixin):
    """
    The IntegerField can be used to set and retrieve integer values. If the
    provided value is not a integer a TypeError will be raised.
    """
    mfn = OpenMaya.MFnNumericAttribute()
    mfn_type = OpenMaya.MFnNumericData.kLong
    default_value = 0

    def __init__(self, min_value=None, max_value=None, **kwargs):
        super(IntegerField, self).__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

        self._validators.append(self.validate_integer)
        if self.min_value is not None:
            self._validators.append(self.validate_min_value)
        if self.max_value is not None:
            self._validators.append(self.validate_max_value)

    # ------------------------------------------------------------------------

    def get_plug_value(self, plug):
        """
        :param OpenMaya.MPlug plug:
        :return: int
        """
        return plug.asInt()

    def set_plug_value(self, modifier, plug, value):
        """
        :param OpenMaya.MDGModifier modifier:
        :param OpenMaya.MPlug plug:
        :param int value:
        """
        modifier.newPlugValueInt(plug, value)

    # ------------------------------------------------------------------------

    @decorator.validator_iterate
    def validate_integer(self, value):
        """
        :raise TypeError: When the value is not a integer.
        """
        if not isinstance(value, int):
            raise TypeError(
                "{} requires a 'int' value, '{}' provided.".format(
                    self.__class__.__name__,
                    type(value).__name__
                )
            )


class FloatField(base.Field, mixin.MinMaxValidatorMixin):
    """
    The FloatField can be used to set and retrieve double values. If the
    provided value is not a float or integer a TypeError will be raised.
    """
    mfn = OpenMaya.MFnNumericAttribute()
    mfn_type = OpenMaya.MFnNumericData.kDouble
    default_value = 0.0

    def __init__(self, min_value=None, max_value=None, **kwargs):
        super(FloatField, self).__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

        self._validators.append(self.validate_int_or_float)
        if min_value is not None:
            self._validators.append(self.validate_min_value)
        if max_value is not None:
            self._validators.append(self.validate_max_value)

    # ------------------------------------------------------------------------

    def get_plug_value(self, plug):
        """
        :param OpenMaya.MPlug plug:
        :return: float
        """
        return plug.asDouble()

    def set_plug_value(self, modifier, plug, value):
        """
        :param OpenMaya.MDGModifier modifier:
        :param OpenMaya.MPlug plug:
        :param float value:
        """
        modifier.newPlugValueDouble(plug, value)

    # ------------------------------------------------------------------------

    @decorator.validator_iterate
    def validate_int_or_float(self, value):
        """
        :raise TypeError: When the value is not an int or float.
        """
        if not isinstance(value, (float, int)):
            raise TypeError(
                "{} requires a 'int/float' value, '{}' provided.".format(
                    self.__class__.__name__,
                    type(value).__name__
                )
            )


class DegreeField(base.Field, mixin.MinMaxValidatorMixin):
    """
    The DegreesField can be used to set and retrieve degree values. If the
    provided value is not a float or integer a TypeError will be raised.
    """
    mfn = OpenMaya.MFnUnitAttribute()
    mfn_type = OpenMaya.MFnUnitAttribute.kAngle
    default_value = 0.0

    def __init__(self, min_value=None, max_value=None, **kwargs):
        super(DegreeField, self).__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

        self._validators.append(self.validate_int_or_float)
        if min_value is not None:
            self._validators.append(self.validate_min_value)
        if max_value is not None:
            self._validators.append(self.validate_max_value)

    # ------------------------------------------------------------------------

    def get_plug_value(self, plug):
        """
        :param OpenMaya.MPlug plug:
        :return: float
        """
        angle = plug.asMAngle()
        return angle.asDegrees()

    def set_plug_value(self, modifier, plug, value):
        """
        :param OpenMaya.MDGModifier modifier:
        :param OpenMaya.MPlug plug:
        :param float value:
        """
        angle = OpenMaya.MAngle(value, OpenMaya.MAngle.kDegrees)
        modifier.newPlugValueMAngle(plug, angle)

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
        default = super(DegreeField, self).default(index)
        if default is None:
            return default
        else:
            return OpenMaya.MAngle(default, OpenMaya.MAngle.kDegrees)

    # ------------------------------------------------------------------------

    @decorator.validator_iterate
    def validate_int_or_float(self, value):
        """
        :raise TypeError: When the value is not an int or float.
        """
        if not isinstance(value, (float, int)):
            raise TypeError(
                "{} requires a 'int/float' value, '{}' provided.".format(
                    self.__class__.__name__,
                    type(value).__name__
                )
            )


class BooleanField(base.Field):
    """
    The BooleanField can be used to set and retrieve bool values. If the
    provided value is not a bool a TypeError will be raised. The boolean field
    will never be able to support a null value. A ValueError will be raised
    when its provided anyway.
    """
    mfn = OpenMaya.MFnNumericAttribute()
    mfn_type = OpenMaya.MFnNumericData.kBoolean
    default_value = True

    def __init__(self, **kwargs):
        super(BooleanField, self).__init__(**kwargs)
        self._validators.append(self.validate_bool)

    # ------------------------------------------------------------------------

    def get_plug_value(self, plug):
        """
        :param OpenMaya.MPlug plug:
        :return: bool
        """
        return plug.asBool()

    def set_plug_value(self, modifier, plug, value):
        """
        :param OpenMaya.MDGModifier modifier:
        :param OpenMaya.MPlug plug:
        :param bool value:
        """
        modifier.newPlugValueBool(plug, value)

    # ------------------------------------------------------------------------

    @decorator.validator_iterate
    def validate_bool(self, value):
        """
        :raise TypeError: When the value is not a boolean.
        """
        if not isinstance(value, bool):
            raise TypeError(
                "{} requires a 'bool' value, '{}' provided.".format(
                    self.__class__.__name__,
                    type(value).__name__
                )
            )


class StringField(base.Field):
    """
    The StringField can be used to set and retrieve string values. If the
    provided value is not a basestring a TypeError will be raised.
    """
    mfn = OpenMaya.MFnTypedAttribute()
    mfn_type = OpenMaya.MFnData.kString
    default_value = ""

    def __init__(self, **kwargs):
        super(StringField, self).__init__(**kwargs)
        self._validators.append(self.validate_basestring)

    # ------------------------------------------------------------------------

    def get_plug_value(self, plug):
        """
        :param OpenMaya.MPlug plug:
        :return: str
        """
        value = plug.asString()
        return value

    def set_plug_value(self, modifier, plug, value):
        """
        :param OpenMaya.MDGModifier modifier:
        :param OpenMaya.MPlug plug:
        :param str value:
        """
        modifier.newPlugValueString(plug, value)

    # ------------------------------------------------------------------------

    def default(self, index=None):
        """
        Default values of string attributes are not stored correctly. The
        default value will be ignored and set once the attribute is added to
        the instance.
        """
        return None

    def add_attribute_to_instance(self, instance):
        """
        Create the field attribute to the instance. This function will take
        the fields settings into account. It is possible to create arrays,
        compounds and all sorts of other attribute types. Because default
        attributes on string attributes do not stick. We set it after the
        attribute is added.

        :param models.Model instance:
        """
        # validate name
        if instance.has_attribute(self.name):
            return

        # add attribute
        attribute = self.create()
        instance.add_attribute(attribute)

        # set attribute default
        plug = instance.get_plug(self.name)
        plug.setString(self.default_value)

    # ------------------------------------------------------------------------

    @decorator.validator_iterate
    def validate_basestring(self, value):
        """
        :raise TypeError: When the value is not a basestring.
        """
        if not isinstance(value, six.string_types):
            raise TypeError(
                "{} requires a 'basestring' value, '{}' provided.".format(
                    self.__class__.__name__,
                    type(value).__name__
                )
            )


class EnumField(base.Field):
    """
    The EnumField can be used to set and retrieve choice values. These values
    can be of any type and are provided in the choices when initializing the
    field. On the node EnumFields will always be stored as integers. But it is
    possible to provide dictionaries or lists too as a choice. If a list is
    provided integer values will automatically be assigned to the return
    value. If a dictionary is provided the integer value is used as a mapper
    between the keys and the values.
    """
    mfn = OpenMaya.MFnEnumAttribute()
    default_value = None

    def __init__(self, choices, **kwargs):
        keys = choices.keys() if isinstance(choices, dict) else choices[:]
        values = choices.values() if isinstance(choices, dict) else choices[:]
        indices = values if all([isinstance(value, int) for value in values]) else range(len(keys))

        self.choices = OrderedDict((str(key), i) for key, i in zip(keys + values, indices * 2))
        self.choices_rev = {i: value for i, value in enumerate(values)}
        self.choices_fields = OrderedDict((key, i) for key, i in zip(keys, indices))
        super(EnumField, self).__init__(choices=self.choices, **kwargs)

    # ------------------------------------------------------------------------

    def get_plug_value(self, plug):
        """
        :param OpenMaya.MPlug plug:
        :return:
        """
        return self.choices_rev[plug.asInt()]

    def set_plug_value(self, modifier, plug, value):
        """
        :param OpenMaya.MDGModifier modifier:
        :param OpenMaya.MPlug plug:
        :param int value:
        """
        index = self.choices[str(value)]
        modifier.newPlugValueInt(plug, index)

    # ------------------------------------------------------------------------

    def default(self, index=None):
        """
        :param int/None index:
        :return: Default value
        :rtype: int/None
        """
        return None

    def create(self):
        """
        :return: Attribute
        :rtype: OpenMaya.MObject
        """
        attribute = super(EnumField, self).create()
        for key, index in self.choices_fields.items():
            self.mfn.addField(key, index)

        default_value = super(EnumField, self).default()
        if default_value is not None:
            self.mfn.default = self.choices.get(default_value, 0)

        return attribute


class MatrixField(base.Field):
    """
    The Matrix can be used to set and retrieve matrix values. The matrix
    can be get/set using the OpenMaya.MMatrix object.
    """
    mfn = OpenMaya.MFnMatrixAttribute()
    mfn_type = OpenMaya.MFnMatrixAttribute.kDouble
    default_value = OpenMaya.MMatrix()

    def __init__(self, **kwargs):
        super(MatrixField, self).__init__(**kwargs)
        self._validators.append(self.validate_matrix)

    # ------------------------------------------------------------------------

    def get_plug_value(self, plug):
        """
        :param OpenMaya.MPlug plug:
        :return: Matrix
        :rtype: OpenMaya.MMatrix
        """
        return OpenMaya.MFnMatrixData(plug.asMObject()).matrix()

    def set_plug_value(self, modifier, plug, value):
        """
        :param OpenMaya.MDGModifier modifier:
        :param OpenMaya.MPlug plug:
        :param OpenMaya.MFnMatrixData/OpenMaya.MMatrix value:
        """
        if not isinstance(value, OpenMaya.MFnMatrixData):
            value = OpenMaya.MFnMatrixData().create(value)

        modifier.newPlugValue(plug, value)

    # ------------------------------------------------------------------------

    @decorator.validator_iterate
    def validate_matrix(self, value):
        """
        :raise TypeError:
            When the value is not either a OpenMaya.MMatrix or
            OpenMaya.MFnMatrixData object.
        """
        if not isinstance(value, OpenMaya.MMatrix) and not isinstance(value, OpenMaya.MFnMatrixData):
            raise TypeError(
                "{} requires a 'OpenMaya.MMatrix/OpenMaya.MFnMatrixData' object, '{}' provided.".format(
                    self.__class__.__name__,
                    type(value).__name__
                )
            )