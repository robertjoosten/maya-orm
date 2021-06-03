from maya.api import OpenMaya

from mango.vendor import apiundo


def execute_modifier(modifier):
    """
    Execute a modifier object. After this the apiundo package is used to
    ensure that the command is undo/redo-able within Maya.

    :param OpenMaya.MDGModifier/OpenMaya.MDagModifier modifier:
    """
    modifier.doIt()
    apiundo.commit(undo=modifier.undoIt, redo=modifier.doIt)


class MDGModifier(object):
    def __init__(self):
        self._modifier = OpenMaya.MDGModifier()

    def __enter__(self):
        return self._modifier

    def __exit__(self, exc_type, exc_val, exc_tb):
        execute_modifier(self._modifier)


class MDagModifier(object):
    def __init__(self):
        self._modifier = OpenMaya.MDagModifier()

    def __enter__(self):
        return self._modifier

    def __exit__(self, exc_type, exc_val, exc_tb):
        execute_modifier(self._modifier)


def get_object(node):
    """
    :param str node:
    :return: Maya object node
    :rtype: OpenMaya.MObject
    """
    sel = OpenMaya.MSelectionList()
    sel.add(node)
    return sel.getDependNode(0)


def get_plug(node):
    """
    :param str node:
    :return: Maya plug node
    :rtype: OpenMaya.MPlug
    """
    sel = OpenMaya.MSelectionList()
    sel.add(node)
    return sel.getPlug(0)


def create_node(node_type, name=None, parent=None):
    """
    :param str node_type:
    :param str/None name:
    :param str/OpenMaya.MObject/None parent:
    :return: Node
    :rtype: OpenMaya.MObject
    """
    # convert parent
    if not parent:
        parent = OpenMaya.MObject.kNullObj
    elif not isinstance(parent, OpenMaya.MObject):
        parent = get_object(parent)

    # create node
    try:
        rename_children = True
        modifier = OpenMaya.MDagModifier()
        m_object = modifier.createNode(node_type, parent)
    except TypeError:
        rename_children = False
        modifier = OpenMaya.MDGModifier()
        m_object = modifier.createNode(node_type)

    # rename node
    if name:
        modifier.renameNode(m_object, name)

    # execute modifier, this needs to happen now as other wise no shape nodes
    # exist and the shapes will not be renamed. The renaming of the shapes
    # will be wrapped in a different modifier.
    execute_modifier(modifier)

    # rename node shapes
    if name and rename_children:
        with MDGModifier() as modifier:
            m_dag_path = OpenMaya.MDagPath.getAPathTo(m_object)
            for index in range(m_dag_path.childCount()):
                modifier.renameNode(
                    m_dag_path.child(index),
                    "{}Shape#".format(name)
                )

    return m_object
