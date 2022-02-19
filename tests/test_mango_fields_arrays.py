from mayaunittest import MayaTestCase

from mango import fields
from mango.models import Model


class TestArrayFields(MayaTestCase):
    def test_integer_array_field(self):
        class TestModel(Model):
            value = fields.IntegerArrayField()

        node = TestModel(name="test")
        self.assertEqual(node.value, [])
        self.assertIsInstance(node.value, list)

        node.value = [0, 0, 0]
        self.assertEqual(len(node.value), 3)

        with self.assertRaises(TypeError):
            node.value = 1

        with self.assertRaises(TypeError):
            node.value = [1.0]

    def test_float_array_field(self):
        class TestModel(Model):
            value = fields.FloatArrayField()

        node = TestModel(name="test")
        self.assertEqual(node.value, [])
        self.assertIsInstance(node.value, list)

        node.value = [0, 0.0, 0.0]
        self.assertEqual(len(node.value), 3)

        with self.assertRaises(TypeError):
            node.value = 1
