from maya import cmds
from mayaunittest import MayaTestCase

from mango import fields
from mango import relations
from mango.models import Model


class TestManagers(MayaTestCase):
    def test_default(self):
        class TestModel(Model):
            pass

        class TestModelInherited(TestModel):
            pass

        TestModel(name="test_1")
        node_2 = TestModel(name="test_2")
        TestModelInherited(name="test_3")
        node_4 = TestModelInherited(name="test_4")
        self.assertEqual(TestModel.objects.length(), 2)
        self.assertEqual(TestModel.objects_typed.length(), 4)

        node_2.delete()
        node_4.delete()
        self.assertEqual(TestModel.objects.length(), 1)
        self.assertEqual(TestModelInherited.objects.length(), 1)

    def test_typed(self):
        class TestModel(Model):
            link_non_typed = relations.OneToOneRel(rev_name="link_non_typed_rev", typed=False)
            link_typed = relations.OneToOneRel(rev_name="link_typed_rev", typed=True)

        class TestModelInherited(TestModel):
            pass

        class TestModelRandom(Model):
            pass

        node_1 = TestModel(name="test_1")
        node_2 = TestModelInherited(name="test_2")
        node_3 = TestModelRandom(name="test_3")

        with self.assertRaises(TypeError):
            node_1.link_non_typed = node_2
        with self.assertRaises(TypeError):
            node_1.link_typed = node_3

    def test_get(self):
        class TestModel(Model):
            link = relations.OneToManyRel(rev_name="link_rev")

        node_1 = TestModel(name="test_1")
        node_2 = TestModel(name="test_2", link=(node_1, ))
        node_1_retrieved = node_2.link.get(name="test_1")
        self.assertEqual(node_1, node_1_retrieved)

    def test_get_or_create(self):
        class TestModel(Model):
            link = relations.OneToManyRel(rev_name="link_rev")

        node_1 = TestModel(name="test_1")
        node_1.link.get_or_create(name="test_2")
        node_1.link.get_or_create(name="test_2")
        self.assertEqual(node_1.link.length(), 1)

    def test_first(self):
        class TestModel(Model):
            link = relations.OneToManyRel(rev_name="link_rev")

        node_1 = TestModel(name="test_1")
        self.assertIsNone(node_1.link.first())
        node_2 = TestModel(name="test_2")
        node_2.link_rev = node_1
        self.assertEqual(node_1.link.first(), node_2)

    def test_filter(self):
        class TestModel(Model):
            value = fields.IntegerField(default_value=0)
            link = relations.OneToManyRel(rev_name="link_rev")

        TestModel(name="test_1", value=1)
        TestModel(name="test_2", value=10)
        TestModel(name="test_3", value=100)
        self.assertEqual(len(TestModel.objects.filter(value=5)), 0)
        self.assertEqual(len(TestModel.objects.filter(value=100)), 1)
        self.assertEqual(len(TestModel.objects.filter(value__ge=10)), 2)

    def test_create(self):
        class TestModel(Model):
            link = relations.OneToManyRel(rev_name="link_rev")

        node_1 = TestModel(name="test_1")
        node_2 = node_1.link.create(name="test_2")
        self.assertEqual(node_1.link.length(), 1)
        self.assertEqual(node_1.link.first(), node_2)

    def test_add(self):
        class TestModel(Model):
            link = relations.OneToManyRel(rev_name="link_rev")

        node_1 = TestModel(name="test_1")
        node_2 = TestModel(name="test_2")
        node_1.link.add(node_2)
        self.assertEqual(node_1.link.length(), 1)

    def test_set(self):
        class TestModel(Model):
            link = relations.OneToManyRel(rev_name="link_rev")

        node_1 = TestModel(name="test_1")
        node_2 = TestModel(name="test_2")
        node_3 = TestModel(name="test_3", link=(node_1, node_2))
        node_3.link.set(node_1)
        self.assertEqual(node_3.link.length(), 1)
        self.assertNotIn(node_2, node_3.link.all())

    def test_remove(self):
        class TestModel(Model):
            link = relations.OneToManyRel(rev_name="link_rev")

        node_1 = TestModel(name="test_1")
        node_2 = TestModel(name="test_2")
        node_3 = TestModel(name="test_3", link=(node_1, node_2))
        node_3.link.remove(node_2)
        self.assertEqual(node_3.link.length(), 1)
        self.assertNotIn(node_2, node_3.link.all())

    def test_clear(self):
        class TestModel(Model):
            link = relations.OneToManyRel(rev_name="link_rev")

        node_1 = TestModel(name="test_1")
        node_2 = TestModel(name="test_2")
        node_3 = TestModel(name="test_3", link=(node_1, node_2))
        node_3.link.clear()
        self.assertEqual(node_3.link.length(), 0)

    def test_all(self):
        class TestModel(Model):
            link = relations.OneToManyRel(rev_name="link_rev")

        node_1 = TestModel(name="test_1")
        node_2 = TestModel(name="test_2", link=(node_1, ))
        self.assertEqual(node_2.link.all(), [node_1])

    def test_length(self):
        class TestModel(Model):
            link = relations.OneToManyRel(rev_name="link_rev")

        node_1 = TestModel(name="test_1")
        node_2 = TestModel(name="test_2", link=(node_1, ))
        self.assertEqual(node_2.link.length(), 1)

    def test_plug_hidden(self):
        class TestModel(Model):
            link = relations.OneToOneRel(rev_name="link_rev", hidden=True)

        node = TestModel(name="test")
        self.assertTrue(cmds.attributeQuery("link", node=node.path, hidden=True))
