from maya.api import OpenMaya

from mango.fields import base
from mango.utils import geometry
from mango.utils import decorator


__all__ = [
    "NurbsCurveField",
    "NurbsCurveArrayField"
]


class NurbsCurveField(base.Field):
    """
    The NurbsCurveField is used to store nurbs curve data. This nurbs curve
    data can be used to generate actual nurbs curves in the scene. The
    return value will be an OpenMaya.MObject that holds reference to
    kNurbsCurveData it can be used to initialize a OpenMaya.MFnNurbsCurve
    object.
    """
    mfn = OpenMaya.MFnTypedAttribute()
    mfn_type = OpenMaya.MFnData.kNurbsCurve
    default_value = geometry.create_curve_data(points=[(0, 0, 0), (0, 1, 0)])

    def __init__(self, **kwargs):
        super(NurbsCurveField, self).__init__(**kwargs)
        self._cache = None
        self._validators.append(self.validate_mfn_nurbs_curve_data)

    # ------------------------------------------------------------------------

    def get_plug_value(self, plug):
        """
        A copy of the data is made to make sure that the data object is not
        accidentally used to alter the data of the curve on the attribute. If
        any edits are made the object can be used to reset the attribute.

        :param OpenMaya.MPlug plug:
        :return: Nurbs curve data object
        :rtype: OpenMaya.MObject
        """
        data_linked = plug.asMObject()
        data_clean = OpenMaya.MFnNurbsCurveData().create()
        OpenMaya.MFnNurbsCurve().copy(data_linked, data_clean)

        return data_clean

    def set_plug_value(self, modifier, plug, value):
        """
        The value is a OpenMaya.MFnNurbsCurve object or a MObject that
        references to an OpenMaya.MFnNurbsCurveData object. The data is
        copied to make sure that any reference to the existing object is
        removed.

        :param OpenMaya.MDGModifier modifier:
        :param OpenMaya.MPlug plug:
        :param OpenMaya.MObject/OpenMaya.MFnNurbsCurve value:
        """
        data = OpenMaya.MFnNurbsCurveData().create()

        if isinstance(value, OpenMaya.MFnNurbsCurve):
            curve = OpenMaya.MFnNurbsCurve()
            curve.create(
                value.cvPositions(),
                value.knots(),
                value.degree,
                value.form,
                False,  # create2D
                False,  # createRational
                data
            )
        else:
            OpenMaya.MFnNurbsCurve().copy(value, data)

        modifier.newPlugValue(plug, data)

    # ------------------------------------------------------------------------

    def get_parent_plug(self, plug):
        """
        When the plug is connected for nurbs curves we can't use the connected
        plug as that is only the output plug. In this case we find the node
        and use its 'create' attribute to create the correct OpenMaya.MPlug
        instance.

        :param OpenMaya.MPlug plug:
        :return: Plug to get/set attribute
        :rtype: OpenMaya.MPlug
        """
        if plug.isDestination:
            plug = plug.source()
            node = plug.node()

            if node.hasFn(OpenMaya.MFn.kNurbsCurve):
                dependency = OpenMaya.MFnDependencyNode(node)
                plug = dependency.findPlug("create", False)

        return plug

    # ------------------------------------------------------------------------

    @decorator.validator_iterate
    def validate_mfn_nurbs_curve_data(self, value):
        """
        :raise TypeError:
            When the value is not either a OpenMaya.MFnNurbsCurve or a
            OpenMaya.MObject with kNurbsCurveData reference.
        """
        m_object_state = isinstance(value, OpenMaya.MObject)
        mfn_nurbs_curve_state = isinstance(value, OpenMaya.MFnNurbsCurve)
        mfn_nurbs_curve_data_state = m_object_state and value.hasFn(OpenMaya.MFn.kNurbsCurveData)
        if not any([mfn_nurbs_curve_state, (m_object_state and mfn_nurbs_curve_data_state)]):
            raise TypeError(
                "{} requires a 'OpenMaya.MFnNurbsCurve' or a 'OpenMaya.MObject' "
                "value with a link to 'kNurbsCurveData', '{}' provided.".format(
                    self.__class__.__name__,
                    type(value).__name__
                )
            )


class NurbsCurveArrayField(NurbsCurveField):
    """
    The NurbsCurveArrayField is used to store an multi of nurbs curve data.
    This nurbs  curve data can be used to generate actual nurbs curves in
    the scene. The return value will be an list of OpenMaya.MObject's that
    holds reference to kNurbsCurveData it can be used to initialize a
    OpenMaya.MFnNurbsCurve object.
    """
    array = True
    default_value = ()
