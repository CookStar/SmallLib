# ../addons/source-python/packages/custom/memorytools/manager.py

"""Provides extended memory functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Core
from core import GameConfigObj
#   Memory
from memory import find_binary
from memory import Convention
from memory import DataType
from memory.helpers import parse_data
from memory.helpers import Key
from memory.helpers import MemberFunction
from memory.helpers import NO_DEFAULT
from memory.manager import manager
from memory.manager import CustomType
from memory.manager import TypeManager

# Memory Tools Imports
#   Memory Tools
from memorytools import get_offset
from memorytools import get_pointer
from memorytools import get_relative_pointer


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("create_type_from_file",
           "get_data_from_dict",
           "get_data_from_file",
           "get_type_from_dict",
           "get_type_from_file",
           "set_type_from_file",
           )


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def function_pointer(
        self, ptr, args=(), return_type=DataType.VOID,
        convention=Convention.THISCALL, doc=None):
    """Create a wrapper for a function."""
    # Automatically add the this pointer argument
    args = (DataType.POINTER,) + tuple(args)

    # Create a converter, if it's not a native type
    if return_type not in DataType.values:
        return_type = self.create_converter(return_type)

    class fget(object):
        def __get__(fget_self, obj, cls):
            # Create the function object
            func = ptr.make_function(
                convention,
                args,
                return_type
            )

            # Called with a this pointer?
            if obj is not None:
                # Wrap the function using MemberFunction, so we don't have
                # to pass the this pointer anymore
                func = MemberFunction(self, return_type, func, obj)

            func.__doc__ = doc
            return func

    return fget()

TypeManager.function_pointer = function_pointer

def create_type_from_file(manager, type_name, file, bases=(CustomType,)):
    return manager(type_name, bases, get_type_from_file(file, manager))

def set_type_from_file(cls, file):
    """Registers a new data to class from a file."""
    for name, value in get_type_from_file(file, cls._manager).items():
        setattr(cls, name, value)

def get_type_from_file(file, manager=manager):
    return get_type_from_dict(GameConfigObj(file), manager)

def get_type_from_dict(raw_data, manager=manager):
    # Prepare general type information
    data = tuple(parse_data(
        manager,
        # Discard all subkeys and add the new dict to a another dict to
        # make it work with parse_data(). Okay, this can be improved...
        {0: dict((k, v) for k, v in raw_data.items() if not isinstance(
            v, dict))},
        (
            (Key.BINARY, Key.as_str, None),
            (Key.SRV_CHECK, Key.as_bool, None),
            (Key.SIZE, Key.as_int, None)
        )
    ))[0][1]

    type_dict = {k:v for k, v in zip(("_binary", "_srv_check", "_size"), data) if v is not None}

    binary = type_dict.get("_binary", None)
    srv_check = type_dict.get("_srv_check", True)

    # Prepare pointer and instance attributes
    for method in (manager.instance_attribute, manager.pointer_attribute):
        attributes = parse_data(
            manager,
            raw_data.get(method.__name__, {}),
            (
                (Key.TYPE_NAME, Key.as_attribute_type, NO_DEFAULT),
                (Key.OFFSET, Key.as_int, NO_DEFAULT),
                (Key.DOC, Key.as_str, None)
            )
        )

        # Create the attributes
        for name, data in attributes:
            type_dict[name] = method(*data)

    # Prepare arrays
    for method in (
            manager.static_instance_array,
            manager.dynamic_instance_array,
            manager.static_pointer_array,
            manager.dynamic_pointer_array):
        arrays = parse_data(
            manager,
            raw_data.get(method.__name__, {}),
            (
                (Key.TYPE_NAME, Key.as_attribute_type, NO_DEFAULT),
                (Key.OFFSET, Key.as_int, NO_DEFAULT),
                (Key.LENGTH, Key.as_int, None),
                (Key.DOC, Key.as_str, None)
            )
        )

        # Create the arrays
        for name, data in arrays:
            type_dict[name] = method(*data)

    # Prepare virtual functions
    vfuncs = parse_data(
        manager,
        raw_data.get("virtual_function", {}),
        (
            (Key.OFFSET, Key.as_int, NO_DEFAULT),
            (Key.ARGS, Key.as_args_tuple, ()),
            (Key.RETURN_TYPE, Key.as_return_type, DataType.VOID),
            (Key.CONVENTION, Key.as_convention, Convention.THISCALL),
            (Key.DOC, Key.as_str, None)
        )
    )

    # Create the virtual functions
    for name, data in vfuncs:
        type_dict[name] = manager.virtual_function(*data)

    # Prepare functions
    funcs = parse_data(
        manager,
        raw_data.get("function", {}),
        (
            (Key.BINARY, Key.as_str, binary if binary is not None else NO_DEFAULT),
            (Key.SRV_CHECK, Key.as_bool, srv_check),
            (Key.IDENTIFIER, Key.as_identifier, NO_DEFAULT),
            (Key.ARGS, Key.as_args_tuple, ()),
            (Key.RETURN_TYPE, Key.as_return_type, DataType.VOID),
            (Key.CONVENTION, Key.as_convention, Convention.THISCALL),
            (Key.DOC, Key.as_str, None)
        )
    )

    # Create the functions
    for name, data in funcs:
        ptr = find_binary(*data[:2]).find_address(data[2])
        type_dict[name] = manager.function_pointer(ptr, *data[:3])

    # Prepare functions
    funcs = parse_data(
        manager,
        raw_data.get("function_pointer", {}),
        (
            (Key.BINARY, Key.as_str, binary if binary is not None else NO_DEFAULT),
            (Key.IDENTIFIER, Key.as_identifier, NO_DEFAULT),
            (Key.OFFSET, Key.as_int, NO_DEFAULT),
            (Key.LEVEL, Key.as_int, 0),
            (Key.SRV_CHECK, Key.as_bool, srv_check),
            (Key.ARGS, Key.as_args_tuple, ()),
            (Key.RETURN_TYPE, Key.as_return_type, DataType.VOID),
            (Key.CONVENTION, Key.as_convention, Convention.THISCALL),
            (Key.DOC, Key.as_str, None)
        )
    )

    # Create the functions
    for name, data in funcs:
        ptr = get_pointer(*data[:5])
        type_dict[name] = manager.function_pointer(ptr, *data[5:])

    # Prepare global pointers
    funcs = parse_data(
        manager,
        raw_data.get("global_pointer", {}),
        (
            (Key.BINARY, Key.as_str, binary if binary is not None else NO_DEFAULT),
            (Key.IDENTIFIER, Key.as_identifier, NO_DEFAULT),
            (Key.OFFSET, Key.as_int, NO_DEFAULT),
            (Key.LEVEL, Key.as_int, 0),
            (Key.SRV_CHECK, Key.as_bool, srv_check)
        )
    )

    # Create the global pointers
    for name, data in funcs:
        type_dict[name] = get_pointer(*data)


    # Via binary.

    # Prepare pointer and instance attributes
    for method in (manager.instance_attribute, manager.pointer_attribute):
        attributes = parse_data(
            manager,
            raw_data.get("binary_"+method.__name__, {}),
            (
                (Key.BINARY, Key.as_str, binary if binary is not None else NO_DEFAULT),
                (Key.IDENTIFIER, Key.as_identifier, NO_DEFAULT),
                (Key.OFFSET, Key.as_int, NO_DEFAULT),
                (Key.SIZE, Key.as_int, 4),
                (Key.SRV_CHECK, Key.as_bool, srv_check),
                (Key.TYPE_NAME, Key.as_attribute_type, NO_DEFAULT),
                (Key.DOC, Key.as_str, None)
            )
        )

        # Create the attributes
        for name, data in attributes:
            offset = get_offset(*data[:5])
            type_dict[name] = method(data[5], offset, data[6])

    # Prepare arrays
    for method in (
            manager.static_instance_array,
            manager.dynamic_instance_array,
            manager.static_pointer_array,
            manager.dynamic_pointer_array):
        arrays = parse_data(
            manager,
            raw_data.get("binary_"+method.__name__, {}),
            (
                (Key.BINARY, Key.as_str, binary if binary is not None else NO_DEFAULT),
                (Key.IDENTIFIER, Key.as_identifier, NO_DEFAULT),
                (Key.OFFSET, Key.as_int, NO_DEFAULT),
                (Key.SIZE, Key.as_int, 4),
                (Key.SRV_CHECK, Key.as_bool, srv_check),
                (Key.TYPE_NAME, Key.as_attribute_type, NO_DEFAULT),
                (Key.LENGTH, Key.as_int, None),
                (Key.DOC, Key.as_str, None)
            )
        )

        # Create the arrays
        for name, data in arrays:
            offset = get_offset(*data[:5])
            type_dict[name] = method(data[5], offset, data[6], data[7])

    # Prepare virtual functions
    vfuncs = parse_data(
        manager,
        raw_data.get("binary_virtual_function", {}),
        (
            (Key.BINARY, Key.as_str, binary if binary is not None else NO_DEFAULT),
            (Key.IDENTIFIER, Key.as_identifier, NO_DEFAULT),
            (Key.OFFSET, Key.as_int, NO_DEFAULT),
            (Key.SIZE, Key.as_int, 4),
            (Key.SRV_CHECK, Key.as_bool, srv_check),
            (Key.ARGS, Key.as_args_tuple, ()),
            (Key.RETURN_TYPE, Key.as_return_type, DataType.VOID),
            (Key.CONVENTION, Key.as_convention, Convention.THISCALL),
            (Key.DOC, Key.as_str, None)
        )
    )

    # Create the virtual functions
    for name, data in vfuncs:
        index = get_offset(*data[:5]) // 4
        type_dict[name] = manager.virtual_function(index, *data[5:])

    # Prepare functions
    funcs = parse_data(
        manager,
        raw_data.get("binary_function", {}),
        (
            (Key.BINARY, Key.as_str, binary if binary is not None else NO_DEFAULT),
            (Key.IDENTIFIER, Key.as_identifier, NO_DEFAULT),
            (Key.OFFSET, Key.as_int, NO_DEFAULT),
            (Key.SIZE, Key.as_int, 4),
            (Key.SRV_CHECK, Key.as_bool, srv_check),
            (Key.ARGS, Key.as_args_tuple, ()),
            (Key.RETURN_TYPE, Key.as_return_type, DataType.VOID),
            (Key.CONVENTION, Key.as_convention, Convention.THISCALL),
            (Key.DOC, Key.as_str, None)
        )
    )

    # Create the functions
    for name, data in funcs:
        ptr = get_relative_pointer(*data[:5])
        type_dict[name] = manager.function_pointer(ptr, *data[5:])

    return type_dict

def get_data_from_file(file):
    return get_data_from_dict(GameConfigObj(file))

def get_data_from_dict(raw_data):
    data_dict = dict()

    data = tuple(parse_data(
        manager,
        {0: dict((k, v) for k, v in raw_data.items() if not isinstance(
            v, dict))},
        (
            (Key.BINARY, Key.as_str, None),
            (Key.SRV_CHECK, Key.as_bool, True)
        )
    ))[0][1]

    binary = data[0]
    srv_check = data[1]


    for method_name in (
            "instance_attribute",
            "pointer_attribute",
            "static_instance_array",
            "dynamic_instance_array",
            "static_pointer_array",
            "dynamic_pointer_array",
            "virtual_function"):
        offsets_data = parse_data(
            manager,
            raw_data.get(method_name, {}),
            (
                (Key.OFFSET, Key.as_int, NO_DEFAULT),
            )
        )

        for name, data in offsets_data:
            data_dict[name] = data[0]


    pointers_data = parse_data(
        manager,
        raw_data.get("function", {}),
        (
            (Key.IDENTIFIER, Key.as_identifier, NO_DEFAULT),
            (Key.BINARY, Key.as_str, binary if binary is not None else NO_DEFAULT),
            (Key.SRV_CHECK, Key.as_bool, srv_check)
        )
    )

    for name, data in pointers_data:
        data_dict[name] = find_binary(*data[1:]).find_address(data[0]).address


    pointers_data = parse_data(
        manager,
        raw_data.get("function_pointer", {}),
        (
            (Key.BINARY, Key.as_str, binary if binary is not None else NO_DEFAULT),
            (Key.IDENTIFIER, Key.as_identifier, NO_DEFAULT),
            (Key.OFFSET, Key.as_int, NO_DEFAULT),
            (Key.LEVEL, Key.as_int, 0),
            (Key.SRV_CHECK, Key.as_bool, srv_check)
        )
    )

    for name, data in pointers_data:
        data_dict[name] = get_pointer(*data).address


    pointers_data = parse_data(
        manager,
        raw_data.get("global_pointer", {}),
        (
            (Key.BINARY, Key.as_str, binary if binary is not None else NO_DEFAULT),
            (Key.IDENTIFIER, Key.as_identifier, NO_DEFAULT),
            (Key.OFFSET, Key.as_int, NO_DEFAULT),
            (Key.LEVEL, Key.as_int, 0),
            (Key.SRV_CHECK, Key.as_bool, srv_check)
        )
    )

    for name, data in pointers_data:
        data_dict[name] = get_pointer(*data).address


    for method_name in (
            "instance_attribute",
            "pointer_attribute",
            "static_instance_array",
            "dynamic_instance_array",
            "static_pointer_array",
            "dynamic_pointer_array",
            "virtual_function"):
        offsets_data = parse_data(
            manager,
            raw_data.get("binary_"+method_name, {}),
            (
                (Key.BINARY, Key.as_str, binary if binary is not None else NO_DEFAULT),
                (Key.IDENTIFIER, Key.as_identifier, NO_DEFAULT),
                (Key.OFFSET, Key.as_int, NO_DEFAULT),
                (Key.SIZE, Key.as_int, 4),
                (Key.SRV_CHECK, Key.as_bool, srv_check)
            )
        )

        for name, data in offsets_data:
            data_dict[name] = get_offset(*data)


    offsets_data = parse_data(
        manager,
        raw_data.get("binary_virtual_function", {}),
        (
            (Key.BINARY, Key.as_str, binary if binary is not None else NO_DEFAULT),
            (Key.IDENTIFIER, Key.as_identifier, NO_DEFAULT),
            (Key.OFFSET, Key.as_int, NO_DEFAULT),
            (Key.SIZE, Key.as_int, 4),
            (Key.SRV_CHECK, Key.as_bool, srv_check)
        )
    )

    for name, data in offsets_data:
        data_dict[name] = get_offset(*data) // 4


    pointers_data = parse_data(
        manager,
        raw_data.get("binary_function", {}),
        (
            (Key.BINARY, Key.as_str, binary if binary is not None else NO_DEFAULT),
            (Key.IDENTIFIER, Key.as_identifier, NO_DEFAULT),
            (Key.OFFSET, Key.as_int, NO_DEFAULT),
            (Key.SIZE, Key.as_int, 4),
            (Key.SRV_CHECK, Key.as_bool, srv_check)
        )
    )

    for name, data in pointers_data:
        data_dict[name] = get_relative_pointer(*data).address

    return data_dict

