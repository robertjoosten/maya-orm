from maya import cmds
from mayaunittest import MayaTestCase

from mango import fields
from mango.models import Model


class TestField(MayaTestCase):
    def test_default_value(self):
        class TestModel(Model):
            value = fields.IntegerField(default_value=5)

        node = TestModel(name="test")
        self.assertEqual(node.value, 5)

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

    def test_choices(self):
        with self.assertRaises(TypeError):
            class TestModelError(Model):
                value = fields.StringField(choices="hello")

        class TestModel(Model):
            value = fields.StringField(choices=("foo", "bar"))

        with self.assertRaises(ValueError):
            TestModel(name="test", value="hello")

        node = TestModel(name="test")
        self.assertEqual(node.value, "foo")

    def test_compound(self):
        class TestModel(Model):
            value = fields.Float3Field()

        node = TestModel(name="test")
        node.value = (1, 1, 1)
        self.assertEqual(node.value, (1, 1, 1))
        with self.assertRaises(ValueError):
            node.value = (0, 0)

    def test_array(self):
        class TestModel(Model):
            value = fields.FloatArrayField()

        node = TestModel(name="test")
        node.value = [1, 1, 1]
        self.assertEqual(len(node.value), 3)

    def test_plug_keyable(self):
        class TestModel(Model):
            value = fields.IntegerField(keyable=True)

        node = TestModel(name="test")
        self.assertTrue(node.get_plug("value").isKeyable)

    def test_plug_channel_box(self):
        class TestModel(Model):
            value_1 = fields.IntegerField(channel_box=True)
            value_2 = fields.IntegerField(keyable=True, channel_box=True)

        node = TestModel(name="test")
        self.assertTrue(node.get_plug("value_1").isChannelBox)
        self.assertTrue(node.get_plug("value_2").isChannelBox)

    def test_plug_hidden(self):
        class TestModel(Model):
            value = fields.IntegerField(hidden=True)

        node = TestModel(name="test")
        self.assertTrue(cmds.attributeQuery("value", node=node.path, hidden=True))