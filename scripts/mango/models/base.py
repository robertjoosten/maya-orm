import six
import logging
import importlib
from functools import wraps
from maya import cmds
from maya.api import OpenMaya
from six.moves.collections_abc import Sequence

from mango import fields
from mango import managers
from mango import relations
from mango.utils import api
from mango.utils import path
from mango.utils import naming
from mango.utils import decorator


__all__ = [
    "Model",
]


RESERVED = {"name", "parent"}
log = logging.getLogger("mango")


def validate_model(func):
    """
    This function is attached to vital function in the Model class. It will
    ensure that the internal node of an instance has not been deleted.
    """
    @wraps(func)
    def wrapper(instance, *args, **kwargs):
        """
        :param Model instance:
        :raise RuntimeError: When the internal node doesn't exist.
        """
        if not instance.exists():
            raise RuntimeError(
                "Unable to run '{}.{}' as its internal node doesn't exist.".format(
                    instance.__class__.__name__,
                    func.__name__
                )
            )

        return func(instance, *args, **kwargs)

    return wrapper


def import_model(type_module, type_name):
    """
    :param str type_module:
    :param str type_name:
    :return: Model type
    :rtype: type
    :raise ImportError: When the model cannot be found.
    """
    try:
        mod = importlib.import_module(type_module)
    except ImportError as e:
        raise ImportError("Import {}.{} failed; {}".format(type_module, type_name, e))

    try:
        type_ = getattr(mod, type_name)
    except AttributeError:
        raise ImportError("Import {0}.{1} failed; No class named {1}".format(type_module, type_name))

    return type_


class ModelMeta(type):
    """
    The model meta class handles the creation of new types and new instances.
    When new types are created is it added the to types and futures type
    dictionaries that can be used to ensure the correct values are retrieved
    by the managers and instance are returned using the correct type. It also
    handles the different constructors that can be used to initialize a model.

    Any instances are being tracked to ensure the type managers are able to
    return all the objects belonging to a certain type including its inherited
    history.

    The path to the type classes are stored on the nodes and will be used to
    import the specific type. An ImportError will be raised when the type
    cannot be imported. If the model itself is used it will not tag the type
    onto the node, this opens up the model to be used to connect but not
    pollute the random node with a specific type.
    """
    fields = None  # type: dict
    relations = None  # type: dict
    node_type = None  # type: str
    _default_manager = None  # type: managers.ManagerDefault
    _default_manager_typed = None  # type: managers.ManagerDefault
    _types = {}
    _types_future = {}
    _instances = {}
    _instances_typed = {}

    def __new__(mcs, name, bases, attrs):
        def get_persisting_objects(obj_key):
            """
            :param str obj_key:
            :return: Persisting objects
            :rtype: dict
            """
            return {
                obj_name: obj
                for base in bases
                for obj_name, obj in getattr(base, obj_key, {}).items()
                if obj.persist and obj_name not in attrs and obj_name not in exclude
            }

        # get persisting data
        exclude = dict.fromkeys(attrs.get("exclude", ()))
        attrs["fields"] = get_persisting_objects("fields")
        attrs["relations"] = get_persisting_objects("relations")

        # get current data
        for key, value in attrs.items():
            # extract fields
            if isinstance(value, fields.Field):
                if key in RESERVED:
                    raise RuntimeError("Field name '{}' is reserved.".format(key))

                value.name = key
                attrs["fields"][key] = value

            # extract relationships
            elif isinstance(value, relations.Relation):
                # get rev name. If the relation is typed we will look at
                # a base relation with a matching name for the rev name.
                # Comes in handy when relation type needs to change or
                # its settings slightly change.
                rev_name = attrs["relations"].get(key, value).rev_name if value.typed else value.rev_name
                rev_name = rev_name if rev_name else value.generate_rev_name(name)

                if key in RESERVED:
                    raise RuntimeError("Relation name '{}' is reserved.".format(key))
                elif rev_name in RESERVED:
                    raise RuntimeError("Relation rev name '{}' is reserved.".format(key))

                value.name = key
                value.rev_name = rev_name
                attrs["relations"][key] = value

                if key in RESERVED:
                    raise

        # create new type
        new_type = super(ModelMeta, mcs).__new__(mcs, name, bases, attrs)
        new_type._default_manager = managers.ManagerDefault(new_type, typed=False)
        new_type._default_manager_typed = managers.ManagerDefault(new_type, typed=True)

        # cache new type and its future
        mcs._types[name] = new_type
        mcs._types_future[name] = []

        for mro in new_type.mro():
            if mcs._types.get(mro.__name__):
                mcs._types_future[mro.__name__].append(name)

        mcs._instances_typed[name] = {}

        # set reverse relationships
        for relation in list(attrs["relations"].values()):
            # skip reverse relations
            if relation.rev:
                continue

            # set cls
            relation.cls = relation.cls or new_type

            # get all reverse types in case it has to be backtracked, this has
            # to be done because we might not be loading all the models before
            # hand.
            if not relation.typed:
                reverse_types = [relation.cls]
            else:
                reverse_types = [
                    mcs._types[name]
                    for name in mcs._types_future[relation.cls.__name__]
                ]

            # set rev relations
            for reverse_type in reverse_types:
                # validate to make sure relation name and reverse name is not
                # omitted in the exclude.
                exclude = set(getattr(reverse_type, "exclude", ()))
                if relation.name in exclude or relation.rev_name in exclude:
                    continue

                # if no reverse type is provided use the same class as was
                # used to create the current type.
                if not reverse_type:
                    reverse_type = new_type

                # if a reverse relation exists it will be updated
                reverse_type_relations = getattr(reverse_type, "relations", {})
                rev_relation = reverse_type_relations.get(relation.rev_name)
                if not rev_relation:
                    rev_relation = relation.rev_relation(
                        new_type,
                        name=relation.rev_name,
                        hidden=relation.rev_hidden,
                        persist=relation.persist,
                        typed=relation.typed,
                    )

                rev_relation.rev = True
                rev_relation.rev_name = relation.name

                # add reverse type
                reverse_type_relations[relation.rev_name] = rev_relation
                setattr(reverse_type, relation.rev_name, rev_relation)

        return new_type

    def __call__(cls, *args, **kwargs):
        def create_node():
            """
            Create the node, the 'name' and 'parent' keyword arguments are
            popped from the keyword arguments dictionary and are used for the
            creation of the node.

            :return: Node
            :rtype: OpenMaya.MObject
            """
            name = kwargs.pop("name", "{}#".format(cls.node_type))
            parent = kwargs.pop("parent", None)

            if isinstance(parent, Model):
                parent = parent.object

            return api.create_node(cls.node_type, name=name, parent=parent)

        def initialize_node():
            """
            Initialize the node from the arguments. If the provided argument
            is not of type OpenMaya.MObject it will be attempted to be
            converted to one. If it fails a RuntimeError will be raised.

            :return: Object and Dependency
            :rtype: tuple(OpenMaya.MObject, OpenMaya.MFnDependencyNode)
            :raise RuntimeError: When node cannot be initialized using arguments
            """
            obj = args[0]
            if isinstance(obj, OpenMaya.MFnDependencyNode):
                return obj.object(), obj
            elif not isinstance(obj, OpenMaya.MObject):
                try:
                    obj = api.get_object(obj)
                except RuntimeError:
                    raise RuntimeError(
                        "Unable to initialize a {} node using the name '{}', "
                        "it doesn't exist.".format(
                            cls.__name__,
                            args[0]
                        )
                    )

            return obj, OpenMaya.MFnDependencyNode(obj)

        # initialize or create node
        if args:
            m_object, mfn_dependency = initialize_node()
            kwargs = {}  # omit any keyword arguments
        else:
            m_object = create_node()
            mfn_dependency = OpenMaya.MFnDependencyNode(m_object)

        # get hex
        handle = OpenMaya.MObjectHandle(m_object)
        hx = "{:02x}".format(handle.hashCode())

        # get cache
        if handle.isValid():
            try:
                node = cls._instances[hx]
                assert node.exists()
            except (KeyError, AssertionError):
                cls._instances.pop(hx, None)
            else:
                return node

        # get type
        has_type = mfn_dependency.hasAttribute("mango")
        if has_type:
            type_value = mfn_dependency.findPlug("mango", False).asString()
            type_module, type_name = type_value.rsplit(".", 1)
            sup = cls._types.get(type_name, import_model(type_module, type_name))
        elif cls != Model:
            attribute_type = OpenMaya.MFnTypedAttribute()
            attribute = attribute_type.create("mango", "mango", OpenMaya.MFnData.kString)
            attribute_type.hidden = True
            mfn_dependency.addAttribute(attribute)

            plug = mfn_dependency.findPlug("mango", False)
            plug.setString("{}.{}".format(cls.__module__, cls.__name__))

            sup = cls
        else:
            sup = cls

        # initialize model
        instance = super(ModelMeta, sup).__call__(hx, m_object, mfn_dependency, **kwargs)
        cls._instances[hx] = instance
        cls._instances_typed[instance.type][hx] = instance

        return instance

    # ------------------------------------------------------------------------

    @property
    def objects(self):
        """
        :return: Default manager
        :rtype: managers.ManagerDefault
        """
        return self._default_manager

    @property
    def objects_typed(self):
        """
        :return: Default manager
        :rtype: managers.ManagerDefault
        """
        return self._default_manager_typed


@six.add_metaclass(ModelMeta)
class Model(object):
    """
    The model is a node which can contain meta data that is attached to the
    model using fields and relations. A model can be created or initialized
    using a variety of constructors.

    Constructors:
        .. code-block:: python

            # create a new model
            Model(**keyword_arguments)

            # initialize an existing node
            Model(str)
            Model(OpenMaya.MObject)
            Model(OpenMaya.MFnDependencyNode)

    When creating a new model the keyword arguments 'name' and 'parent' are
    always present and can be used. Any other arguments are dependant on the
    fields and relations added to the model class.
    """
    fields = None  # type: dict
    relations = None  # type: dict
    node_type = "network"

    def __init__(self, *args, **kwargs):
        # variables
        self._exists = True
        self._callbacks = []
        self._hx, self._m_object, self._mfn_dependency = args

        # add relations
        for key, relation in self.relations.items():
            manager = relation.add_manager_to_instance(self)
            if key in kwargs:
                values = kwargs.pop(key) if key in kwargs else None
                values = values if isinstance(values, Sequence) else [values]
                manager.set(*values)

        # add fields
        for key, field in self.fields.items():
            field.add_attribute_to_instance(self)
            if key in kwargs:
                value = kwargs.pop(key)
                field.set(self, value, initialize=True)

        # error when there are left over keyword arguments, when errors are
        # present the node is deleted.
        if kwargs:
            self.delete()
            raise TypeError(
                "{}.__init__() got unexpected keyword argument(s) '{}'.".format(
                    self.__class__.__name__,
                    "', '".join(kwargs.keys())
                )
            )

        # create callbacks
        self.create_callback(
            OpenMaya.MNodeMessage.addNodeDestroyedCallback,
            self.object,
            self._emit_deleted,
            None
        )

        self.create_callback(
            OpenMaya.MNodeMessage.addNodeAboutToDeleteCallback,
            self.object,
            self._emit_deleted,
            None
        )

    # ------------------------------------------------------------------------

    def __eq__(self, other):
        """
        :param Base other:
        :return: Equal state
        :rtype: bool
        """
        return isinstance(other, Model) and self.object == other.object

    def __ne__(self, other):
        """
        :param Base other:
        :return: Not equal state
        :rtype: bool
        """
        return isinstance(other, Model) and self.object != other.object

    def __repr__(self):
        """
        :return: Repr
        :rtype: str
        """
        return "<{}.{} instance '{}'>".format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.name if self.exists() else "invalid"
        )

    # ------------------------------------------------------------------------

    def _emit_deleted(self, *args, **kwargs):
        """
        Change the deleted variable so the exists function gives an accurate
        representation of the nodes state in the scene. This also removed any
        callbacks attached to the node.
        """
        # remove callbacks and caches on instance
        self._exists = False
        self.delete_cache()
        self.delete_callbacks()

        # remove caches on class
        cls = self.__class__
        getattr(cls, "_instances").pop(self.hx, None)
        getattr(cls, "_instances_typed")[cls.__name__].pop(self.hx, None)

    # ------------------------------------------------------------------------

    @property
    def hx(self):
        """
        :return: Hex
        :rtype: str
        """
        return self._hx

    @property
    def uuid(self):
        """
        :return: UUID
        :rtype: str
        """
        return self.dependency.uuid().asString()

    # ------------------------------------------------------------------------

    @property
    def name(self):
        """
        :return: Name
        :rtype: str
        """
        return self.dependency.name()

    @property
    def namespace(self):
        """
        :return: Namespace
        :rtype: str/None
        """
        return naming.get_namespace(self.name)

    @property
    def leaf_name(self):
        """
        :return: Name
        :rtype: str
        """
        return naming.get_leaf_name(self.name)

    def rename(self, name):
        """
        :param str name:
        """
        # create namespace
        namespace = naming.get_namespace(name)
        if namespace:
            if not cmds.namespace(exists=namespace):
                cmds.namespace(add=namespace)

        # rename node
        with api.MDGModifier() as modifier:
            modifier.renameNode(self.object, name)

    # ------------------------------------------------------------------------

    @property
    def path(self):
        """
        :return: Partial path
        :rtype: str
        """
        return path.get(self.object, full_path=False)

    @property
    def full_path(self):
        """
        :return: Full path
        :rtype: str
        """
        return path.get(self.object, full_path=True)

    def exists(self):
        """
        :return: Node exists
        :rtype: bool
        """
        return self._exists

    def is_referenced(self):
        """
        :return: Node referenced
        :rtype: bool
        """
        return self.dependency.isFromReferencedFile

    # ------------------------------------------------------------------------

    @property
    def type(self):
        """
        :return: Type
        :rtype: str
        """
        return self.__class__.__name__

    @property
    @validate_model
    def object(self):
        """
        :return: Object
        :rtype: OpenMaya.MObject
        """
        return self._m_object

    @property
    @validate_model
    def dependency(self):
        """
        :return: Dependency
        :rtype: OpenMaya.MFnDependency
        """
        return self._mfn_dependency

    # ------------------------------------------------------------------------

    def has_attribute(self, name):
        """
        :param str name:
        :return: If node has the attribute
        :raise: bool
        """
        return self.dependency.hasAttribute(name)

    @decorator.memoize
    def get_attribute(self, name):
        """
        :param str name:
        :return: Attribute
        :rtype: OpenMaya.MObject
        """
        return self.dependency.attribute(name)

    def add_attribute(self, attribute):
        """
        :param OpenMaya.MObject attribute:
        """
        # clear attribute from cache
        attribute_fn = OpenMaya.MFnAttribute(attribute)
        self.pop_cache(attribute_fn.name)
        self.pop_cache(attribute_fn.shortName)

        # add attribute
        with api.MDGModifier() as modifier:
            modifier.addAttribute(self.object, attribute)

    def delete_attribute(self, name):
        """
        Delete the provided attribute from the node. If the attribute doesn't
        exist no warning is presented as the attribute is not there which is
        the goal of the function. When deleting attributes the get attribute
        cache is cleared to make sure that plugs can be retrieved correctly.

        :param str name:
        """
        # validate attribute
        if not self.has_attribute(name):
            return

        # remove attribute
        attribute = self.get_attribute(name)
        attribute_fn = OpenMaya.MFnAttribute(attribute)

        # clear attribute from cache
        self.pop_cache(attribute_fn.name)
        self.pop_cache(attribute_fn.shortName)

        # remove attribute
        with api.MDGModifier() as modifier:
            modifier.setNodeLockState(self.object, False)
            modifier.removeAttribute(self.object, attribute)

    # ------------------------------------------------------------------------

    @decorator.memoize
    def get_plug(self, name):
        """
        :param str name:
        :return: Plug
        :rtype: OpenMaya.MPlug
        :raise RuntimeError: When the attribute doesn't exist on the node.
        """
        try:
            node = path.get(self.object, full_path=True)
            return api.get_plug("{}.{}".format(node, name))
        except RuntimeError:
            raise RuntimeError(
                "Attribute '{}' doesn't exist on node '{}'.".format(
                    name,
                    self.dependency.name()
                )
            )

    # ------------------------------------------------------------------------

    def create_callback(self, callback, *args, **kwargs):
        """
        :param callback:
        :return: Callback ID
        :rtype: int
        """
        id_ = callback(*args, **kwargs)
        self._callbacks.append(id_)
        return id_

    def delete_callbacks(self):
        """
        Remove the callbacks from the node. This can come in handy when
        clearing a cache and or when the node gets deleted to make sure there
        are no unnecessary callbacks floating around.
        """
        if self._callbacks:
            OpenMaya.MMessage.removeCallbacks(self._callbacks)
            self._callbacks = []

    # ------------------------------------------------------------------------

    def pop_cache(self, item):
        """
        Pop an attribute name from the cache list. This function will remove
        the attribute from both the attribute and plug list to keep them both
        up to date.

        :param str item:
        """
        self.get_attribute.pop(self, item)
        self.get_plug.pop(self, item)

    def delete_cache(self):
        """
        Delete the cache from any functions that have a memoize decorator
        attached to them.
        """
        self.get_attribute.clear()
        self.get_plug.clear()

    # ------------------------------------------------------------------------

    def clear(self):
        """
        Remove any meta data and meta data tags from the node. This will allow
        the node to be re-initialized using a different class.
        """
        for name in self.fields:
            self.delete_attribute(name)

        for name in self.relations:
            self.delete_attribute(name)

        if self.has_attribute("mango"):
            self.delete_attribute("mango")

        # invalidate node by deleting the callbacks and removing the instance
        # from the caches.
        self._emit_deleted()

    def delete(self):
        """
        Remove the node. The node is unlocked to make sure that it is allowed
        to be deleted. Any callbacks will automatically be triggered.
        """
        with api.MDGModifier() as modifier:
            modifier.setNodeLockState(self.object, False)
            modifier.deleteNode(self.object)
