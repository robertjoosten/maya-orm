from maya.api import OpenMaya

from mango.utils import api


def get(node, full_path=True):
    """
    Get the path from a variety of possible inputs. This will reduce a lot
    of if statements when working with maya paths.

    :param str/OpenMaya.MObject node:
    :param bool full_path:
    :return: str
    :raise RuntimeError: When the path doesn't exist in the current scene.
    """
    # convert node to object
    if not isinstance(node, OpenMaya.MObject):
        node = api.get_object(node)

    # extract path
    if node.hasFn(OpenMaya.MFn.kDagNode):
        dag = OpenMaya.MDagPath.getAPathTo(node)
        path = dag.fullPathName() if full_path else dag.partialPathName()
    else:
        dep = OpenMaya.MFnDependencyNode(node)
        path = dep.name()

    # validate path
    if not path:
        raise RuntimeError(
            "Unable to construct path from provided node '{}'.".format(node)
        )

    return path
