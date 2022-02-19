from maya.api import OpenMaya
from mayaunittest import MayaTestCase

from mango import fields
from mango.models import Model
from mango.utils import geometry


class TestGeometryFields(MayaTestCase):
    def test_nurbs_curve_field(self):
        class TestModel(Model):
            value = fields.NurbsCurveField()

        node = TestModel(name="test")
        curve = node.value  # requires local
        curve_fn = OpenMaya.MFnNurbsCurve(curve)
        self.assertEqual(curve_fn.numCVs, 2)
        self.assertEqual(curve_fn.degree, 1)

        curve = geometry.create_curve_data(degree=3, points=[(0, i, 0) for i in range(2)])
        node.value = curve

        curve = node.value  # requires local
        curve_fn = OpenMaya.MFnNurbsCurve(curve)
        self.assertEqual(curve_fn.numCVs, 4)
        self.assertEqual(curve_fn.degree, 3)

        with self.assertRaises(TypeError):
            node.value = None

    def test_nurbs_curve_array_field(self):
        class TestModel(Model):
            value = fields.NurbsCurveArrayField()

        node = TestModel(name="test")
        self.assertEqual(node.value, [])
        self.assertIsInstance(node.value, list)

        curve = geometry.create_curve_data(degree=3, points=[(0, i, 0) for i in range(3)])
        node.value = [curve, curve]
        self.assertEqual(len(node.value), 2)

        with self.assertRaises(TypeError):
            node.value = curve
