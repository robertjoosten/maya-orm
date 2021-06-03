"""
Django inspired metadata framework for Maya.

Installation
============

* Extract the content of the .rar file anywhere on disk.
* Drag the mango.mel file in Maya to permanently install the script.

Usage
=====

The userSetup.py registers callbacks that will automatically process the scene
when a file gets Imported/Opened or a reference gets Created/Loaded. This will
allow instant easy access to the models.

Models
======

Create
------

A model can be created by inheriting from a base class. Fields and relations
can be added to the class using descriptors. There is a wide variety of
fields and relations to choose from. Both fields and relations have base
classes that can be inherited from to generate new types.
::
    from mango import models
    from mango import fields
    from mango import relations

    class Joint(models.Model):
        node_type = "joint"
        number = fields.IntegerField(default_value=10, keyable=True)
        link = relations.OneToManyRel(rev_name="link_reverse", typed=True)

    class Collection(models.Model):
        node_type = "transform"
        joint_set = relations.OneToManyRel(Joint, rev_name="part", typed=True)

Initialize
----------

Once the class is created you can either initialize a model by creating a
new node calling the class using keyword arguments or you can initialize an
existing node by provided the name of the node. In both events attributes for
the fields and relations are created.
::
    # create new nodes
    l_elbow_jnt = Joint(name="l_elbow_jnt", number=1)
    l_wrist_jnt = Joint(name="l_wrist_jnt", parent="l_elbow_jnt", link=l_elbow_jnt)

    # initialize existing nodes
    l_elbow_jnt = Joint("l_elbow_jnt")  # initialize using string
    l_elbow_jnt = Joint(l_elbow_jnt.object)  # initialize using OpenMaya.MObject
    l_elbow_jnt = Joint(l_elbow_jnt.dependency)  # initialize using OpenMaya.MFnDependencyNode

Fields
======

Fields can be retrieved and set using the descriptor. Validators are attached
to each field to ensure values can actually be set on the node.
::
    print(l_elbow_jnt.number)
    l_elbow_jnt.number = 5
    l_elbow_jnt.number = "10"  # raises TypeError

Relations
=========

Relations can be retrieved and set using the descripter. Validators are
attached to each relation to make sure that only the right typed models are
added as relations.
::
    print(l_elbow_jnt.link_reverse)
    print(l_wrist_jnt.link.all())
    l_elbow_jnt.link_reverse = None
    l_wrist_jnt.link.add(l_elbow_jnt)

Managers
========

Manager objects are attached to the model types and to the relations. Only
when a relation is not singular a manager object will be returned. This
manager object can be used to Create/Set/Add and Remove model instances.
::
    l_shoulder_joint = Joint.objects.create(name="l_shoulder_jnt")
    print(Joint.objects.all())
    print(Joint.objects.filter(number=10))  # operators allowed using '__'

"""
import sys
import pkgutil
import importlib


def refresh():
    """
    The refresh function removed any mango modules from the sys modules
    dictionary. Before doing this any existing callbacks will be removed as
    they will be recreated once models are initialized.

    If any classes inherit from mango but do not live in the package the
    inheritance will be broken. Those modules will have to be reloaded as well
    but that is up to the user to organise.
    """
    # remove callbacks
    from mango import models
    for model in models.Model.objects.all():
        model.delete_callbacks()

    # delete modules
    modules = set()
    for module_name in list(sys.modules.keys()):
        if module_name.startswith(__name__):
            del sys.modules[module_name]
            modules.add(module_name)

    # import modules
    for loader, module_name, is_pkg in pkgutil.walk_packages(__path__, "{}.".format(__name__)):
        if module_name in modules:
            importlib.import_module(module_name)
