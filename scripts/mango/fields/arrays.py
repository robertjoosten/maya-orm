from maya.api import OpenMaya

from mango.fields import generic


__all__ = [
    "IntegerArrayField",
    "FloatArrayField",
]


class IntegerArrayField(generic.IntegerField):
    """
    The IntegerArrayField can be used to set and retrieve int multi values. If the
    provided value is not a list containing integer values a TypeError will be
    raised.
    """
    array = True
    default_value = None

    def __init__(self, *args, **kwargs):
        super(IntegerArrayField, self).__init__(*args, **kwargs)
        self._validators[-1] = self.validate_child_is_int

    # ------------------------------------------------------------------------

    def validate_child_is_int(self, value):
        """
        :raise TypeError: When the value is not a list.
        """
        for value_ in value:
            if not isinstance(value_, int):
                raise TypeError(
                    "{} requires 'int' values inside of the 'list/tuple', '{}' provided.".format(
                        self.__class__.__name__,
                        type(value_).__name__
                    )
                )


class FloatArrayField(generic.FloatField):
    """
    The FloatArrayField can be used to set and retrieve double multi values.
    If the provided value is not a list containing float or integer values a
    TypeError will be raised.
    """
    array = True
    default_value = None

    def __init__(self, *args, **kwargs):
        super(FloatArrayField, self).__init__(*args, **kwargs)
        self._validators[-1] = self.validate_child_is_int_or_float

    # ------------------------------------------------------------------------

    def validate_child_is_int_or_float(self, value):
        """
        :raise TypeError: When the value is not a list.
        """
        for value_ in value:
            if not isinstance(value_, (float, int)):
                raise TypeError(
                    "{} requires 'int/float' values inside of the 'list/tuple', '{}' provided.".format(
                        self.__class__.__name__,
                        type(value_).__name__
                    )
                )
