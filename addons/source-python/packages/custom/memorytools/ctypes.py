# ../addons/source-python/packages/custom/memorytools/ctypes.py

"""Provides a helper feature for ctypes."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Ctypes
import ctypes

# Source.Python Imports
#   Core
from core import AutoUnload
from core import PLATFORM
#   Memory
from memory import alloc
from memory import Convention
from memory import DataType

# Memory Tools Imports
#   Memory Tools
from memorytools.conventions import CDECL_RETURN4
from memorytools.conventions import FASTCALL_CALLER


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("get_ctype_argtypes",
           "get_ctype_calling_convention",
           "get_ctype_from_data_type",
           "get_ctype_function",
           "Base_Ctypes",
           "Ctypes_CDECL",
           "Ctypes_FASTCALL",
           "Ctypes_FASTCALL_CALLER",
           "Ctypes_THISCALL",
           "Ctypes_STDCALL",
           )


# =============================================================================
# >> CLASSES
# =============================================================================
class Base_Ctypes(AutoUnload):
    def __init__(self, address, argtypes, restype, auto_dealloc=True):
        functype = ctypes.CFUNCTYPE(restype, *argtypes)

        size = self.get_size(argtypes)
        op_codes = self.make_asm(int(address), size, argtypes, restype)
        op_codes_size = len(op_codes)

        self.memory = alloc(op_codes_size, auto_dealloc)
        self.memory.unprotect(op_codes_size)
        ctypes.memmove(ctypes.c_void_p(self.memory.address), op_codes, op_codes_size)

        self.function = functype(self.memory.address)

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def _unload_instance(self):
        self.memory.dealloc()

    @staticmethod
    def get_size(argtypes):
        raise NotImplementedError("Needs to be implemented by a sub class.")

    @staticmethod
    def make_asm(address, size, argtypes, restype):
        raise NotImplementedError("Needs to be implemented by a sub class.")


class Ctypes_CDECL:
    def __init__(self, address, argtypes, restype, auto_dealloc=True):
        functype = ctypes.CFUNCTYPE(restype, *argtypes)
        self.function = functype(int(address))

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)


class Ctypes_STDCALL(Ctypes_CDECL):
    def __init__(self, address, argtypes, restype, auto_dealloc=True):
        functype = ctypes.WINFUNCTYPE(restype, *argtypes)
        self.function = functype(int(address))


class Ctypes_THISCALL(Base_Ctypes):

    @staticmethod
    def get_size(argtypes):
        size = 0
        for argtype in argtypes[1:]:
            sizeof_argtype = ctypes.sizeof(argtype)
            if sizeof_argtype >= 4:
                size += sizeof_argtype
            else:
                size += 4

        return size

    @staticmethod
    def make_asm(address, size, argtypes, restype):
        op_codes = []
        op_codes.extend([0x8b, 0x4c, 0x24, 0x04])           #   mov     ecx, [esp+4]
        for i in range(0, size, 4):
            op_codes.extend([0xff, 0x74, 0x24, size+4])     #   push	dword[esp+size+4]
        op_codes.extend([0xb8])
        op_codes.extend((address).to_bytes(4, "little"))    #   mov     eax, address
        op_codes.extend([0xff, 0xd0])                       #   call    eax
        op_codes.extend([0xc3])                             #   ret
        return bytes(op_codes)


class Ctypes_FASTCALL(Base_Ctypes):

    @staticmethod
    def get_size(argtypes):
        size = 0
        skip = True
        for index, argtype in enumerate(argtypes):
            sizeof_argtype = ctypes.sizeof(argtype)

            if index == 1:
                if sizeof_argtype > 4:
                    skip = False
                continue

            if index == 2 and skip:
                continue

            if sizeof_argtype >= 4:
                size += sizeof_argtype
            else:
                size += 4

        return size

    @staticmethod
    def make_asm(address, size, argtypes, restype):
        op_codes = []
        op_codes.extend([0x8b, 0x4c, 0x24, 0x04])           #   mov     ecx, [esp+4]
        op_codes.extend([0x8b, 0x54, 0x24, 0x08])           #   mov     edx, [esp+8]
        for i in range(0, size, 4):
            op_codes.extend([0xff, 0x74, 0x24, size+8])     #   push	dword[esp+size+8]
        op_codes.extend([0xb8])
        op_codes.extend((address).to_bytes(4, "little"))    #   mov     eax, address
        op_codes.extend([0xff, 0xd0])                       #   call    eax
        op_codes.extend([0xc3])                             #   ret
        return bytes(op_codes)


class Ctypes_FASTCALL_CALLER(Ctypes_FASTCALL):

    @staticmethod
    def make_asm(address, size, argtypes, restype):
        op_codes = []
        op_codes.extend([0x8b, 0x4c, 0x24, 0x04])           #   mov     ecx, [esp+4]
        op_codes.extend([0x8b, 0x54, 0x24, 0x08])           #   mov     edx, [esp+8]
        for i in range(0, size, 4):
            op_codes.extend([0xff, 0x74, 0x24, size+8])     #   push	dword[esp+size+8]
        op_codes.extend([0xb8])
        op_codes.extend((address).to_bytes(4, "little"))    #   mov     eax, address
        op_codes.extend([0xff, 0xd0])                       #   call    eax
        op_codes.extend([0x83, 0xc4, size])                 #   add     esp, size
        op_codes.extend([0xc3])                             #   ret
        return bytes(op_codes)


class Ctypes_DELPHI_MODIFIED(Base_Ctypes):

    @staticmethod
    def get_size(argtypes):
        return 0

    @staticmethod
    def make_asm(address, size, argtypes, restype):
        op_codes = []
        op_codes.extend([0x8b, 0x44, 0x24, 0x04])           #   mov     eax, [esp+4]
        op_codes.extend([0x8b, 0x54, 0x24, 0x08])           #   mov     edx, [esp+8]
        op_codes.extend([0xb9])
        op_codes.extend((address).to_bytes(4, "little"))    #   mov     ecx, address
        op_codes.extend([0xff, 0xd1])                       #   call    ecx
        op_codes.extend([0xc3])                             #   ret
        return bytes(op_codes)


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def get_ctype_function(function, calling_convention=None, auto_dealloc=True):
    address = function.trampoline.address if function.is_hooked() else function.address
    argtypes = get_ctype_argtypes(*function.arguments)
    restype = get_ctype_from_data_type(function.return_type)

    if calling_convention is None:
        if function.convention != Convention.CUSTOM:
            calling_convention = get_ctype_calling_convention(
                function.convention)
        elif isinstance(function.custom_convention, CDECL_RETURN4):
            calling_convention = Ctypes_CDECL
        elif isinstance(function.custom_convention, FASTCALL_CALLER):
            calling_convention = Ctypes_FASTCALL_CALLER
        else:
            raise ValueError("Calling convention is not specified.")

    return calling_convention(address, argtypes, restype, auto_dealloc)

if PLATFORM == "linux":
    _ctype_calling_convention = {
        Convention.CDECL: Ctypes_CDECL,
        Convention.THISCALL: Ctypes_CDECL,
    }
else:
    _ctype_calling_convention = {
        Convention.CDECL: Ctypes_CDECL,
        Convention.THISCALL: Ctypes_THISCALL,
        Convention.STDCALL: Ctypes_STDCALL,
        Convention.FASTCALL: Ctypes_FASTCALL,
    }

def get_ctype_calling_convention(calling_convention):
    try:
        return _ctype_calling_convention[calling_convention]
    except KeyError:
        raise ValueError("Given calling_convention is not supported.")

def get_ctype_argtypes(*argtypes):
    ctype_argtypes = list()
    for data_type in argtypes:
        ctype_argtypes.append(get_ctype_from_data_type(data_type))
    return tuple(ctype_argtypes)

_ctype_data_type = {
    DataType.VOID: None,
    DataType.BOOL: ctypes.c_bool,
    DataType.CHAR: ctypes.c_char,
    DataType.UCHAR: ctypes.c_ubyte,
    DataType.SHORT: ctypes.c_short,
    DataType.USHORT: ctypes.c_ushort,
    DataType.INT: ctypes.c_int,
    DataType.UINT: ctypes.c_uint,
    DataType.LONG: ctypes.c_long,
    DataType.ULONG: ctypes.c_ulong,
    DataType.LONG_LONG: ctypes.c_longlong,
    DataType.ULONG_LONG: ctypes.c_ulonglong,
    DataType.FLOAT: ctypes.c_float,
    DataType.DOUBLE: ctypes.c_double,
    DataType.POINTER: ctypes.c_void_p,
    DataType.STRING: ctypes.c_char_p
}

def get_ctype_from_data_type(data_type):
    try:
        return _ctype_data_type[data_type]
    except KeyError:
        raise ValueError("Given data_type is not supported.")

