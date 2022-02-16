from maya import cmds
from maya.api import OpenMaya
from mayaunittest import MayaTestCase

from mango import fields
from mango.models import Model


class TestFieldsBase(MayaTestCase):
    def test_default_value(self):
        class TestModel(Model):
            value = fields.IntegerField(default_value=5)

        node = TestModel(name="test")
        self.assertEqual(node.value, 5)

    def test_min_value(self):
        class TestModel(Model):
            value = fields.IntegerField(min_value=0)

        node = TestModel(name="test")
        with self.assertRaises(ValueError):
            node.value = -1

    def test_max_value(self):
        class TestModel(Model):
            value = fields.IntegerField(max_value=0)

        node = TestModel(name="test")
        with self.assertRaises(ValueError):
            node.value = 1

    def test_editable(self):
        class TestModel(Model):
            value = fields.IntegerField(editable=False)

        node = TestModel(name="test")
        with self.assertRaises(RuntimeError):
            node.value = 1

    def test_default_value_only(self):
        class TestModel(Model):
            value = fields.IntegerField(default_value=0, default_value_only=True)

        with self.assertRaises(RuntimeError):
            TestModel(name="test", value=1)

        node = TestModel(name="test", value=0)
        with self.assertRaises(RuntimeError):
            node.value = 1