import re


def upper_camel_to_snake_case(name):
    """
    :param str name:
    :return: Snake case name
    :rtype: str
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
