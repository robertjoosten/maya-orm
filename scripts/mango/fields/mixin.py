from mango.utils import decorator


class MinMaxValidatorMixin(object):
    min_value = None
    max_value = None

    @decorator.validator_iterate
    def validate_min_value(self, value):
        """
        :raise ValueError:
            When the value is smaller than the provided min value.
        """
        if self.min_value is not None and self.min_value > value:
            raise ValueError(
                "{} value '{}' is smaller than minimum value '{}'".format(
                    self.__class__.__name__,
                    value,
                    self.max_value
                )
            )

    @decorator.validator_iterate
    def validate_max_value(self, value):
        """
        :raise ValueError:
            When the value is larger than the provided max value.
        """
        if self.max_value is not None and self.max_value < value:
            raise ValueError(
                "{} value '{}' is bigger than maximum value '{}'".format(
                    self.__class__.__name__,
                    value,
                    self.max_value
                )
            )