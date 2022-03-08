from maya import cmds
from mayaunittest import MayaTestCase

from mango import relations
from mango.models import Model


class TestRelations(MayaTestCase):
    def test_one_to_one(self):
        class TestModel(Model):
            link = relations.OneToOneRel(rev_name="link_rev")

        node_1 = TestModel(name="test_1")
        node_2 = TestModel(name="test_2")
        node_3 = TestModel(name="test_3")

        node_1.link = node_2
        self.assertEqual(node_1.link, node_2)
        self.assertEqual(node_2.link_rev, node_1)

        node_3.link = node_2
        self.assertIsNone(node_1.link)
        self.assertEqual(node_3.link, node_2)
        self.assertEqual(node_2.link_rev, node_3)

    def test_one_to_many(self):
        class TestModel(Model):
            link = relations.OneToManyRel(rev_name="link_rev")

        node_1 = TestModel(name="test_1")
        node_2 = TestModel(name="test_2")
        node_3 = TestModel(name="test_3")
        node_4 = TestModel(name="test_4")

        node_1.link.add(node_2)
        node_3.link_rev = node_1
        self.assertEqual(node_1.link.length(), 2)
        self.assertIn(node_2, node_1.link.all())
        self.assertEqual(node_2.link_rev, node_1)

        node_4.link.add(node_2)
        node_3.link_rev = node_4
        self.assertEqual(node_1.link.length(), 0)
        self.assertEqual(node_4.link.length(), 2)
        self.assertIn(node_2, node_4.link.all())
        self.assertEqual(node_2.link_rev, node_4)

        with self.assertRaises(RuntimeError):
            node_1.link = node_2

    def test_many_to_one(self):
        class TestModel(Model):
            link = relations.ManyToOneRel(rev_name="link_rev")

        node_1 = TestModel(name="test_1")
        node_2 = TestModel(name="test_2")
        node_3 = TestModel(name="test_3")
        node_4 = TestModel(name="test_4")

        node_1.link_rev.add(node_2)
        node_3.link = node_1
        self.assertEqual(node_1.link_rev.length(), 2)
        self.assertIn(node_2, node_1.link_rev.all())
        self.assertEqual(node_2.link, node_1)

        node_4.link_rev.add(node_2)
        node_3.link = node_4
        self.assertEqual(node_1.link_rev.length(), 0)
        self.assertEqual(node_4.link_rev.length(), 2)
        self.assertIn(node_2, node_4.link_rev.all())
        self.assertEqual(node_2.link, node_4)

        with self.assertRaises(RuntimeError):
            node_1.link_rev = node_2

    def test_many_to_many(self):
        class TestModel(Model):
            link = relations.ManyToManyRel(rev_name="link_rev")

        node_1 = TestModel(name="test_1")
        node_2 = TestModel(name="test_2")
        node_3 = TestModel(name="test_3")
        node_4 = TestModel(name="test_4")

        node_1.link.add(node_2)
        node_3.link_rev.add(node_1)
        self.assertEqual(node_1.link.length(), 2)
        self.assertEqual(node_2.link_rev.length(), 1)
        self.assertIn(node_2, node_1.link.all())
        self.assertIn(node_1, node_2.link_rev.all())

        node_4.link.add(node_2)
        self.assertEqual(node_4.link.length(), 1)
        self.assertEqual(node_2.link_rev.length(), 2)
        self.assertIn(node_2, node_4.link.all())
        self.assertIn(node_4, node_2.link_rev.all())

        with self.assertRaises(RuntimeError):
            node_1.link_rev = node_2
        with self.assertRaises(RuntimeError):
            node_1.link = node_2

    def test_collection(self):
        class TestModel(Model):
            link_single = relations.Collection(multi=False)
            link_multi = relations.Collection(multi=True)

        transform_1 = cmds.createNode("transform", name="transform_1")
        node_1 = TestModel(name="test_1")
        node_2 = TestModel(name="test_2")
        node_3 = TestModel(name="test_3")

        node_1.link_single = node_2
        node_1.link_multi.add(node_2, node_3)
        self.assertEqual(node_1.link_single, node_2)
        self.assertIn(node_2, node_1.link_multi.all())
        self.assertIn(node_3, node_1.link_multi.all())

        node_1.link_single = transform_1
        self.assertEqual(node_1.link_single.path, transform_1)
        self.assertIsInstance(node_1.link_single, Model)

        with self.assertRaises(RuntimeError):
            node_1.link_multi = node_2
