import re


def upper_camel_to_snake_case(name):
    """
    :param str name:
    :return: Snake case name
    :rtype: str
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


# ----------------------------------------------------------------------------


def get_name(node_name):
    """
    :param str node_name:
    :return: Name
    :rtype: str
    """
    return node_name.rsplit("|", 1)[-1]


def get_leaf_name(node_name):
    """
    :param str node_name:
    :return: Leaf name
    :rtype: str
    """
    return get_name(node_name).rsplit(":", 1)[-1]


def get_namespace(node_name):
    """
    :param str node_name:
    :return: Namespace
    :rtype: str
    """
    if ":" in node_name:
        name = get_name(node_name)
        return name.rsplit(":", 1)[0]
