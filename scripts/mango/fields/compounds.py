from mango.fields import generic


__all__ = [
    "Float2Field",
    "Float3Field",
    "Degree3Field",
    "Boolean3Field",
]


class Float2Field(generic.FloatField):
    """
    The Float2Field can be used to set and retrieve double compound values.
    If the provided value is not a list containing float or integer values a
    TypeError will be raised. The fixed length of the compound is 2.
    """
    compound = "UV"
    default_value = (0.0, 0.0)


class Float3Field(generic.FloatField):
    """
    The Float3Field can be used to set and retrieve double compound values.
    If the provided value is not a list containing float or integer values a
    TypeError will be raised. The fixed length of the multi is 3.
    """
    compound = "XYZ"
    default_value = (0.0, 0.0, 0.0)


class Degree3Field(generic.DegreeField):
    """
    The Degree3Field can be used to set and retrieve angle compound values.
    If the provided value is not a list containing float or integer values a
    TypeError will be raised. The fixed length of the multi is 3.
    """
    compound = "XYZ"
    default_value = (0.0, 0.0, 0.0)


class Boolean3Field(generic.BooleanField):
    """
    The Boolean3Field can be used to set and retrieve boolean compound values.
    If the provided value is not a list containing boolean values a TypeError
    will be raised. The fixed length of the multi is 3.
    """
    compound = "XYZ"
    default_value = (True, True, True)
