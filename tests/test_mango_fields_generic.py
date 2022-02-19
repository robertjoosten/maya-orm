from six import string_types
from maya.api import OpenMaya
from mayaunittest import MayaTestCase

from mango import fields
from mango.models import Model


class TestGenericFields(MayaTestCase):
    def test_integer_field(self):
        class TestModel(Model):
            value = fields.IntegerField()

        node = TestModel(name="test", value=0)
        self.assertEqual(node.value, 0)
        self.assertIsInstance(node.value, int)

        node.value = 1
        self.assertEqual(node.value, 1)

        with self.assertRaises(TypeError):
            node.value = 1.0

    def test_float_field(self):
        class TestModel(Model):
            value = fields.FloatField()

        node = TestModel(name="test", value=0.0)
        self.assertEqual(node.value, 0.0)
        self.assertIsInstance(node.value, float)

        node.value = 1.0
        node.value = 1
        self.assertEqual(node.value, 1.0)

        with self.assertRaises(TypeError):
            node.value = "1"

    def test_degree_field(self):
        class TestModel(Model):
            value = fields.DegreeField()

        node = TestModel(name="test", value=0.0)
        self.assertEqual(node.value, 0.0)
        self.assertIsInstance(node.value, float)

        node.value = 1.0
        node.value = 1
        self.assertEqual(node.value, 1.0)

        with self.assertRaises(TypeError):
            node.value = "1"

    def test_boolean_field(self):
        class TestModel(Model):
            value = fields.BooleanField()

        node = TestModel(name="test", value=False)
        self.assertEqual(node.value, False)
        self.assertIsInstance(node.value, bool)

        node.value = True
        self.assertEqual(node.value, True)

        with self.assertRaises(TypeError):
            node.value = None

    def test_string_field(self):
        class TestModel(Model):
            value = fields.StringField()

        node = TestModel(name="test", value="foo")
        self.assertEqual(node.value, "foo")
        self.assertIsInstance(node.value, string_types)

        node.value = "bar"
        self.assertEqual(node.value, "bar")

        with self.assertRaises(TypeError):
            node.value = None

    def test_enum_field(self):
        class TestModel(Model):
            value_1 = fields.EnumField(default_value="bar", choices=("foo", "bar"))
            value_2 = fields.EnumField(choices={"foo": 0, "bar": 1})

        node = TestModel(name="test", value_1="foo", value_2="foo")
        self.assertEqual(node.value_1, "foo")
        self.assertEqual(node.value_2, 0)

        node.value_1 = "bar"
        node.value_2 = "bar"
        self.assertEqual(node.value_1, "bar")
        self.assertEqual(node.value_2, 1)

        with self.assertRaises(ValueError):
            node.value_1 = "hello"

    def test_matrix_field(self):
        class TestModel(Model):
            value = fields.MatrixField()

        node = TestModel(name="test")
        self.assertTrue(node.value.isEquivalent(OpenMaya.MMatrix()))
        self.assertIsInstance(node.value, OpenMaya.MMatrix)

        with self.assertRaises(TypeError):
            node.value = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
