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

    def __init__(self, *args, **kwargs):
        super(Float2Field, self).__init__(*args, **kwargs)
        self._validators.pop()
        self._validators.append(self.validate_length)
        self._validators.append(self.validate_child_is_int_or_float)

    # ------------------------------------------------------------------------

    def validate_length(self, value):
        """
        :raise ValueError: When the value is not a list.
        """
        value_length = len(value)
        if value_length != 2:
            raise ValueError(
                "{} requires a 'list/tuple' with a length of 2.".format(
                    self.__class__.__name__,
                )
            )

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


class Float3Field(generic.FloatField):
    """
    The Float3Field can be used to set and retrieve double compound values.
    If the provided value is not a list containing float or integer values a
    TypeError will be raised. The fixed length of the multi is 3.
    """
    compound = "XYZ"
    default_value = (0.0, 0.0, 0.0)

    def __init__(self, *args, **kwargs):
        super(Float3Field, self).__init__(*args, **kwargs)
        self._validators.pop()
        self._validators.append(self.validate_length)
        self._validators.append(self.validate_child_is_int_or_float)

    # ------------------------------------------------------------------------

    def validate_length(self, value):
        """
        :raise ValueError: When the value is not a list.
        """
        value_length = len(value)
        if value_length != 3:
            raise ValueError(
                "{} requires a 'list/tuple' with a length of 3.".format(
                    self.__class__.__name__,
                )
            )

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


class Degree3Field(generic.DegreeField):
    """
    The Degree3Field can be used to set and retrieve angle compound values.
    If the provided value is not a list containing float or integer values a
    TypeError will be raised. The fixed length of the multi is 3.
    """
    compound = "XYZ"
    default_value = (0.0, 0.0, 0.0)

    def __init__(self, *args, **kwargs):
        super(Degree3Field, self).__init__(*args, **kwargs)
        self._validators.pop()
        self._validators.append(self.validate_length)
        self._validators.append(self.validate_child_is_int_or_float)

    # ------------------------------------------------------------------------

    def validate_length(self, value):
        """
        :raise ValueError: When the value is not a list.
        """
        value_length = len(value)
        if value_length != 3:
            raise ValueError(
                "{} requires a 'list/tuple' with a length of 3.".format(
                    self.__class__.__name__,
                )
            )

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


class Boolean3Field(generic.BooleanField):
    """
    The Boolean3Field can be used to set and retrieve boolean compound values.
    If the provided value is not a list containing boolean values a TypeError
    will be raised. The fixed length of the multi is 3.
    """
    compound = "XYZ"
    default_value = (True, True, True)

    def __init__(self, *args, **kwargs):
        super(Boolean3Field, self).__init__(*args, **kwargs)
        self._validators.pop()
        self._validators.append(self.validate_length)
        self._validators.append(self.validate_child_is_bool)

    # ------------------------------------------------------------------------

    def validate_length(self, value):
        """
        :raise ValueError: When the value is not a list.
        """
        value_length = len(value)
        if value_length != 3:
            raise ValueError(
                "{} requires a 'list/tuple' with a length of 3.".format(
                    self.__class__.__name__,
                )
            )

    def validate_child_is_bool(self, value):
        """
        :raise TypeError: When the value is not a list.
        """
        for value_ in value:
            if not isinstance(value_, bool):
                raise TypeError(
                    "{} requires 'bool' values inside of the 'list/tuple', '{}' provided.".format(
                        self.__class__.__name__,
                        type(value_).__name__
                    )
                )