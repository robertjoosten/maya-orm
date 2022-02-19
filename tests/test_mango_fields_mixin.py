from mayaunittest import MayaTestCase

from mango import fields
from mango.models import Model


class TestMinMaxValidatorMixin(MayaTestCase):
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
