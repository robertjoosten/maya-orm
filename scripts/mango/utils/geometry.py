from maya.api import OpenMaya


def create_curve_data(points, degree=1, form=OpenMaya.MFnNurbsCurve.kOpen, knots=None):
    """
    Create a curve data object, this data object can be used together with
    the NurbsCurveField and the generation of its default values. This data
    object can be initialized as a OpenMaya.MFnNurbsCurve by calling the
    following command.

    Example:
        .. code-block:: python

            mfn_nurbs_curve_data = create_curve_data(points=[[0, 0, 0], [0, 1, 0], degree=1])
            mfn_nurbs_curve = OpenMaya.MFnNurbsCurve(mfn_nurbs_curve_data)
            print(mfn_nurbs_curve.degree)

    :param list[tuple] points:
    :param int degree:
    :param int form:
    :param list[int]/None knots:
    :return: Curve data
    :rtype: OpenMaya.MObject
    """
    data = OpenMaya.MFnNurbsCurveData().create()
    curve = OpenMaya.MFnNurbsCurve()

    if knots is None:
        curve.createWithEditPoints(
            points,
            degree,
            form,
            False,  # create2D
            False,  # createRational
            True,  # uniformParam
            data
        )
    else:
        curve.create(
            points,
            knots,
            degree,
            form,
            False,  # create2D
            False,  # createRational
            data
        )

    return data


def create_circle_data(
        sections=8,
        degree=3,
        radius=1,
        sweep=360,
        normal=(0, 0, 1),
        center=(0, 0, 0)
):
    """
    Create a curve data object, this data object can be used together with
    the NurbsCurveField and the generation of its default values. This data
    object can be initialized as a OpenMaya.MFnNurbsCurve. This function is
    a helper function to easily creating a circle.

    :param int sections:
    :param int degree: 1 or 3
    :param int/float radius:
    :param int/float sweep:
    :param tuple(int/float) normal:
    :param tuple(int/float) center:
    :return: Circle data
    :rtype: OpenMaya.MObject
    """
    modifier = OpenMaya.MDGModifier()
    obj = modifier.createNode("makeNurbCircle")
    dependency = OpenMaya.MFnDependencyNode(obj)
    modifier.newPlugValueInt(dependency.findPlug("sections", False), sections)
    modifier.newPlugValueInt(dependency.findPlug("degree", False), degree)
    modifier.newPlugValueDouble(dependency.findPlug("radius", False), radius)
    modifier.newPlugValueDouble(dependency.findPlug("sweep", False), sweep)
    modifier.newPlugValueDouble(dependency.findPlug("normalX", False), normal[0])
    modifier.newPlugValueDouble(dependency.findPlug("normalY", False), normal[1])
    modifier.newPlugValueDouble(dependency.findPlug("normalZ", False), normal[2])
    modifier.newPlugValueDouble(dependency.findPlug("centerX", False), center[0])
    modifier.newPlugValueDouble(dependency.findPlug("centerY", False), center[1])
    modifier.newPlugValueDouble(dependency.findPlug("centerZ", False), center[2])

    try:
        modifier.doIt()
        data = OpenMaya.MFnNurbsCurveData().create()
        data_linked = dependency.findPlug("outputCurve", False).asMObject()
        OpenMaya.MFnNurbsCurve().copy(data_linked, data)
    finally:
        modifier.undoIt()

    return data