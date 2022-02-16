from maya import cmds
from maya.api import OpenMaya
from mayaunittest import MayaTestCase

from mango.models import Model


class TestModels(MayaTestCase):
    def test_create(self):
        _ = Model(name="test")
        self.assertTrue(cmds.objExists("test"))

    def test_initialize(self):
        cmds.createNode("network", name="test")
        node = Model("test")
        self.assertTrue(node.exists())

        with self.assertRaises(RuntimeError):
            Model("test_not_existing")

    def test_equal(self):
        node_1 = Model(name="test_1")
        node_2 = Model(name="test_2")
        self.assertEqual(node_1, node_1)
        self.assertNotEqual(node_1, node_2)

    def test_name(self):
        node = Model(name="test")
        self.assertEqual(node.name, "test")

    def test_leaf_name(self):
        node = Model(name="test")
        node_namespace = Model(name="hello:test")
        self.assertEqual(node.leaf_name, "test")
        self.assertEqual(node_namespace.leaf_name, "test")

    def test_namespace(self):
        node = Model(name="test")
        node_namespace = Model(name="hello:test")
        self.assertIsNone(node.namespace)
        self.assertEqual(node_namespace.namespace, "hello")

    def test_rename(self):
        node = Model(name="test")
        node.rename("test_renamed")
        self.assertEqual(node.name, "test_renamed")

        node.rename("test:test_renamed")
        self.assertEqual(node.name, "test:test_renamed")

    def test_path(self):
        cmds.createNode("transform", name="container")
        cmds.createNode("transform", name="test", parent="container")
        cmds.createNode("transform", name="test", parent="test")
        node = Model("|container|test|test")
        self.assertEqual(node.path, "container|test|test")
        self.assertEqual(node.full_path, "|container|test|test")

    def test_exists(self):
        node = Model(name="test")
        self.assertTrue(node.exists())
        cmds.delete("test")
        self.assertFalse(node.exists())

    def test_is_referenced(self):
        node = Model(name="test")
        self.assertFalse(node.is_referenced())

        reference_path = self.get_temp_path("reference.ma")
        cmds.file(rename=reference_path)
        cmds.file(save=True, force=True, type="mayaAscii")
        cmds.file(newFile=True, force=True)
        cmds.file(reference_path, reference=True, namespace="hello")

        node = Model("hello:test")
        self.assertTrue(node.is_referenced())

    def test_type(self):
        node = Model(name="test")
        self.assertEqual(node.type, "Model")

    def test_clear(self):
        class TestModel(Model):
            pass

        node = TestModel(name="test")
        self.assertTrue(cmds.attributeQuery("mango", node="test", exists=True))

        node.clear()
        self.assertFalse(cmds.attributeQuery("mango", node="test", exists=True))

    def test_delete(self):
        node = Model(name="test")
        node.delete()
        self.assertFalse(cmds.objExists("test"))

    def test_has_attribute(self):
        node = Model(name="test")
        self.assertFalse(node.has_attribute("test"))
        self.assertTrue(node.has_attribute("message"))

    def test_get_attribute(self):
        node = Model(name="test")
        attribute = node.get_attribute("message")
        self.assertTrue(attribute.hasFn(OpenMaya.MFn.kMessageAttribute))

    def test_add_attribute(self):
        node = Model(name="test")
        attribute = OpenMaya.MFnMessageAttribute().create("test", "test")
        node.add_attribute(attribute)
        self.assertTrue(cmds.attributeQuery("test", node="test", exists=True))

    def test_delete_attribute(self):
        node = Model(name="test")
        cmds.addAttr(node.path, longName="test")
        node.delete_attribute("test")
        self.assertFalse(cmds.attributeQuery("test", node="test", exists=True))

    def test_get_plug(self):
        node = Model(name="test")
        plug = node.get_plug("message")
        self.assertIsInstance(plug, OpenMaya.MPlug)

        with self.assertRaises(RuntimeError):
            node.get_plug("test")
