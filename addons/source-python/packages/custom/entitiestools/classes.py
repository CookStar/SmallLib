# ../addons/source-python/packages/custom/entitiestools/classes.py

"""Provides access to many objects for entities."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Collections
from collections import defaultdict
#   Inspect
from inspect import currentframe
#   Pathlib
from pathlib import Path
#   Warnings
from warnings import warn

# Site-Packages Imports
#   ConfigObj
from configobj import Section

# Source.Python Imports
#   Core
from core import GameConfigObj
#from core.dumps import _get_datamaps
#   Entities
from entities.classes import server_classes
from entities.classes import _managers_path
from entities.classes import _supported_keyvalue_types
from entities.datamaps import FieldType
from entities.entity import BaseEntity
from entities.factories import factory_dictionary
#   Paths
from paths import CUSTOM_DATA_PATH
from paths import CUSTOM_PACKAGES_PATH
from paths import PLUGIN_PATH
#   Listeners
from listeners import on_entity_created_listener_manager
#from listeners import on_tick_listener_manager

# Memory Tools Imports
#   Memory Tools
from memorytools.manager import get_data_from_file
from memorytools.manager import get_type_from_file


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("get_entities_data",
           "load_entities_data",
           )


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
#datamaps = dict()
data_paths = defaultdict(set)

# ../addons/source-python/data/custom/entities
ENTITIES_DATA_PATH = Path(CUSTOM_DATA_PATH / "entities")


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def get_caller_directory():
    frame = currentframe().f_back.f_back

    filename = frame.f_code.co_filename
    path = Path(filename)

    if filename.startswith(PLUGIN_PATH):
        dir = path.relative_to(PLUGIN_PATH).parts[0]
    elif filename.startswith(CUSTOM_PACKAGES_PATH):
        dir = path.relative_to(CUSTOM_PACKAGES_PATH).parts[0]

    return dir

def get_entities_data(base_entity, dir=None):
    if dir is None:
        dir = get_caller_directory()

    path = ENTITIES_DATA_PATH / dir

    entity_data = dict()
    entity_server_classes = [server_class.__name__ for server_class in reversed(server_classes.get_entity_server_classes(base_entity))]
    for class_name in entity_server_classes:
        file_name = class_name + ".ini"
        entity_data.update(get_data_from_file(_managers_path / file_name))
        entity_data.update(get_data_from_file(str(path / file_name)))

    return entity_data

def load_entities_data(dir=None):
    if dir is None:
        dir = get_caller_directory()

    data_path = ENTITIES_DATA_PATH / dir
    if data_path.exists() and data_path.is_dir():
        for path in data_path.rglob("*.ini"):
            data_paths[path.stem].add(str(data_path / path.name))
    else:
        raise ValueError("Invalid data path: {path}".format(path=data_path))

    for classname in factory_dictionary:
        base_entity = BaseEntity.find(classname)
        if base_entity is not None:
            datamap = base_entity.datamap
            while datamap:
                class_name = datamap.class_name
                if class_name not in server_classes:
                    server_classes._get_server_class(class_name, datamap)
                datamap = datamap.base

    update_data()

    if (data_paths and
        on_entity_created not in on_entity_created_listener_manager):
        on_entity_created_listener_manager.register_listener(on_entity_created)

def update_data():
    for class_name, paths in list(data_paths.items()):
        server_class = server_classes.get(class_name, None)
        if server_class is None:
            continue

        for path in paths:
            raw_data = GameConfigObj(path)
            set_server_class(raw_data, server_class, class_name)
            for name, value in get_type_from_file(raw_data, server_classes).items():
                setattr(server_class, name, value)

        del data_paths[class_name]

    if (not data_paths and
        on_entity_created in on_entity_created_listener_manager):
        on_entity_created_listener_manager.unregister_listener(on_entity_created)

def set_server_class(raw_data, server_class, class_name):
    for name, value in raw_data.get("input", {}).items():
        setattr(server_class, name, server_class.inputs[value])

    for name, value in raw_data.get("property", {}).items():
        if isinstance(value, Section):
            property = server_class.properties[value["name"]]
            setattr(server_class, name, server_classes.entity_property(
                value["type"], property.offset, property.networked))
        else:
            property = server_class.properties[value]
            setattr(server_class, name, server_classes.entity_property(
                property.prop_type, property.offset, property.networked))

    for name, value in raw_data.get("keyvalue", {}).items():
        if isinstance(value, Section):
            keyvalue_name = value["name"]
            if keyvalue_name in server_class.keyvalues:
                warn("KeyValue \"{name}\" already implemented.".format(name=keyvalue_name))
                continue

            keyvalue_type = getattr(FieldType, value["type"])
            supported_type = _supported_keyvalue_types.get(keyvalue_type, None)
            if supported_type is None:
                warn("Unsupported KeyValue type \"{type}\".".format(type=keyvalue_type))
                continue

            server_class.keyvalues[keyvalue_name] = {"name":keyvalue_name, "type":value["type"], "alias":name}
            setattr(server_class, name, server_classes.keyvalue(keyvalue_name, supported_type))
        else:
            keyvalue = server_class.keyvalues[value]
            keyvalue_type = keyvalue.type
            supported_type = _supported_keyvalue_types.get(keyvalue_type, None)
            if supported_type is None:
                warn("Unsupported KeyValue type \"{type}\".".format(type=keyvalue_type))
                continue

            setattr(server_class, name, server_classes.keyvalue(value, supported_type))


    # Loop through all based attributes
    for name, data in raw_data.get("based_attribute", {}).items():

        # Resolve the method to register this attribute
        method = getattr(server_classes, data.get("method", "instance_attribute"))

        # Resolve the offset of this attribute
        offset = Key.as_int(
            server_classes,
            data.get("offset_" + PLATFORM, data.get("offset", 0))
        )

        # Resolve the base offset of this attribute
        base = data.get("base_" + PLATFORM, data.get("base"))
        try:
            offset += server_class.properties[base].offset
        except KeyError:
            raise NameError(
                f"\"{base}\" is not a valid property " +
                f"for attribute \"{class_name}.{name}\"."
            )

        # Generate the attribute
        attribute = method(
            Key.as_attribute_type(server_classes, data["type"]),
            offset,
            data.get("doc")
        )

        # Assign the attribute to the server_class
        setattr(server_class, name, attribute)


# =============================================================================
# >> LISTENERS
# =============================================================================
def on_entity_created(base_entity):
    server_classes.get_entity_server_classes(base_entity)
    update_data()

"""
def on_tick():
    if not datamaps:
        datamaps.update(_get_datamaps())
    on_tick_listener_manager.unregister_listener(on_tick)
    on_entity_created_listener_manager.unregister_listener(on_entity_created)

on_tick_listener_manager.register_listener(on_tick)
"""

