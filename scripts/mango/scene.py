import time
import logging
from maya.api import OpenMaya

from mango import models
from mango.utils import api


log = logging.getLogger("mango")


def initialize():
    """
    The initialization of a current scene find any object with a mango
    attribute and initialize its class. This will place it in memory and
    speed up the loading times. If the initialization of the model fails a
    warning message will be presented to the user.
    """
    t = time.time()
    initialized = 0

    iterator = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kDependencyNode)
    while not iterator.isDone():
        m_object = iterator.thisNode()
        mfn_dependency = OpenMaya.MFnDependencyNode(m_object)

        if mfn_dependency.hasAttribute("mango"):
            try:
                models.Model(mfn_dependency)
                initialized += 1
            except (RuntimeError, ImportError) as e:
                log.warning("Unable to initialize node '{}'; {}".format(
                    mfn_dependency.name(),
                    str(e)
                ))

        iterator.next()

    delta = time.time() - t
    log.info("Initialized {} models in {:.3f} seconds.".format(initialized, delta))


def migrate():
    """
    Types are stored by name in memory but the module is stored in the mango
    attribute so the class doesn't have to be in memory for it to work as it
    gets imported when needed. When class' move it is possible for this module
    path to be incorrect. This function will loop over all models initialized
    in the scene and reset the mango attribute and validate its assigned
    fields and relations.
    """
    def migrate_type():
        with api.MDGModifier() as modifier:
            modifier.newPlugValueString(plug, new_value)

        log.info("Migrate type '{}.mango'; invalid import.".format(
            model.dependency.name()
        ))

    def migrate_field(message):
        """
        :param str message:
        """
        model.delete_attribute(field.name)
        field.add_attribute_to_instance(model)
        log.info("Migrate field '{}.{}'; {}.".format(
            model.name,
            field.name,
            message
        ))

    def migrate_relation(message):
        """
        :param str message:
        """
        model.delete_attribute(relation.name)
        relation.add_manager_to_instance(model)
        log.info("Migrate relation '{}.{}'; {}.".format(
            model.name,
            relation.name,
            message
        ))

    t = time.time()

    # migrate models
    for model in models.Model.objects.all():
        cls = model.__class__

        # migrate type
        plug = model.get_plug("mango")
        old_value = plug.asString()
        new_value = "{}.{}".format(cls.__module__, cls.__name__)
        if old_value != new_value:
            migrate_type()

        # migrate fields
        for field in cls.fields.values():
            # validate parent plug
            plug = model.get_plug(field.name)
            if plug.isArray is not field.multi:
                migrate_field("incorrect multi")
                continue
            elif plug.isCompound is not bool(field.compound):
                migrate_field("incorrect compound")
                continue
            elif plug.isCompound and plug.numChildren() != len(field.compound or []):
                migrate_field("incorrect compound number")
                continue

            # validate component plug
            plug = plug.child(0) if plug.isCompound else plug
            attribute = plug.attribute()

            if attribute.apiType() != field.mfn.type():
                migrate_field("incorrect attribute type")
                continue

            field.mfn.setObject(attribute)
            if attribute.hasFn(OpenMaya.MFn.kNumericAttribute) and field.mfn.numericType() is not field.mfn_type:
                migrate_field("incorrect numeric attribute type")
                continue
            elif attribute.hasFn(OpenMaya.MFn.kTypedAttribute) and field.mfn.attrType() is not field.mfn_type:
                migrate_field("incorrect typed attribute type")
                continue

            # TODO: update default value
            # TODO: update hidden
            # TODO: update keyable
            # TODO: update channel box

        # migrate relations
        for relation in cls.relations.values():
            plug = model.get_plug(relation.name)
            attribute = plug.attribute()
            attribute_fn = OpenMaya.MFnAttribute(attribute)

            if plug.isArray is not relation.multi:
                migrate_relation("incorrect multi")
                continue
            elif attribute_fn.writable is not relation.rev:
                migrate_relation("incorrect direction")
                continue

            # TODO: update hidden

    delta = time.time() - t
    log.info("Migrated models in {:.3f} seconds.".format(delta))
