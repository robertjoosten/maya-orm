import logging
from maya.api import OpenMaya


log = logging.getLogger("mango")


def initialize(*args, **kwargs):
    """
    The initialize function is a wrapper to the initialize function in the
    mango. As it is possible the entire mango package to get reloaded the
    import statement is done in the function itself.
    """
    from mango import scene
    scene.initialize()


def register_scene_callbacks():
    """
    Register a scene callbacks that process the current scene when triggered.
    The current scene will be read and all mango models initialized.
    """
    OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterImport, initialize)
    OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterOpen, initialize)
    OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterCreateReference, initialize)
    OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterLoadReference, initialize)
    log.info("Scene callbacks registered.")


register_scene_callbacks()
