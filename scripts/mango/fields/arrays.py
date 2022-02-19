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


class FloatArrayField(generic.FloatField):
    """
    The FloatArrayField can be used to set and retrieve double multi values.
    If the provided value is not a list containing float or integer values a
    TypeError will be raised.
    """
    array = True
    default_value = None
