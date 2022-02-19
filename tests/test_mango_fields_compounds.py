from mayaunittest import MayaTestCase

from mango import fields
from mango.models import Model


class TestCompoundFields(MayaTestCase):
    def test_float_2_field(self):
        class TestModel(Model):
            value = fields.Float2Field()

        node = TestModel(name="test")
        self.assertEqual(node.value, (0.0, 0.0))
        self.assertIsInstance(node.value, tuple)

        node.value = (1, 1)
        self.assertEqual(len(node.value), 2)

        with self.assertRaises(TypeError):
            node.value = 1

        with self.assertRaises(ValueError):
            node.value = (0.0, )

    def test_float_3_field(self):
        class TestModel(Model):
            value = fields.Float3Field()

        node = TestModel(name="test")
        self.assertEqual(node.value, (0.0, 0.0, 0.0))
        self.assertIsInstance(node.value, tuple)

        node.value = (1, 1, 1)
        self.assertEqual(len(node.value), 3)

        with self.assertRaises(TypeError):
            node.value = 1

        with self.assertRaises(ValueError):
            node.value = (0.0, )

    def test_degree_3_field(self):
        class TestModel(Model):
            value = fields.Degree3Field()

        node = TestModel(name="test")
        self.assertEqual(node.value, (0.0, 0.0, 0.0))
        self.assertIsInstance(node.value, tuple)

        node.value = (1, 1, 1)
        self.assertEqual(len(node.value), 3)

        with self.assertRaises(TypeError):
            node.value = 1

        with self.assertRaises(ValueError):
            node.value = (0.0, )

    def test_boolean_3_field(self):
        class TestModel(Model):
            value = fields.Boolean3Field()

        node = TestModel(name="test")
        self.assertEqual(node.value, (True, True, True))
        self.assertIsInstance(node.value, tuple)

        node.value = (False, False, False)
        self.assertEqual(len(node.value), 3)

        with self.assertRaises(TypeError):
            node.value = True

        with self.assertRaises(ValueError):
            node.value = (True, )
