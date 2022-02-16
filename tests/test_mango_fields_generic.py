from maya import cmds
from maya.api import OpenMaya
from mayaunittest import MayaTestCase

from mango import fields
from mango.models import Model


class TestFieldsGeneric(MayaTestCase):
    def test_integer_field(self):
        class TestModel(Model):
            value = fields.IntegerField()

        node = TestModel(name="test", value=5)
        self.assertEqual(node.value, 5)
        self.assertIsInstance(node.value, int)

        node.value = 10
        self.assertEqual(node.value, 10)

        with self.assertRaises(TypeError):
            node.value = "10"
