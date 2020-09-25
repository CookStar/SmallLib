# ../ctypes.py

"""Provides a helper feature for ctypes."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Ctypes
import ctypes

# Source.Python
#   Core
from core import PLATFORM
#   Memory
from memory import alloc
from memory import Convention
from memory import DataType


# =============================================================================
# >> CLASSES
# =============================================================================
class CDECL:
    def __init__(self, address, argtypes, restype, auto_dealloc=True):
        functype = ctypes.CFUNCTYPE(restype, *argtypes)
        self.ctype = functype(address)

    def __call__(self, *args, **kwargs):
        return self.ctype(*args, **kwargs)


class STDCALL(CDECL):
    def __init__(self, address, argtypes, restype, auto_dealloc=True):
        functype = ctypes.WINFUNCTYPE(restype, *argtypes)
        self.ctype = functype(address)


class THISCALL(CDECL):
    def __init__(self, address, argtypes, restype, auto_dealloc=True):
        functype = ctypes.CFUNCTYPE(restype, *argtypes)

        op_codes = self.make_asm(argtypes, address)
        op_codes_size = len(op_codes)

        self.memory = alloc(op_codes_size, auto_dealloc)
        self.memory.unprotect(op_codes_size)
        for offset, op_code in enumerate(op_codes):
            self.memory.set_uchar(op_code, offset)

        self.ctype = functype(self.memory.address)

    def make_asm(self, argtypes, address):
        size = self.get_size(argtypes)
        op_codes = []
        op_codes.extend([0x8b, 0x4c, 0x24, 0x04])           #   mov     ecx, [esp+4]
        for i in range(0, size, 4):
            op_codes.extend([0xff, 0x74, 0x24, size+4])     #   push	dword[esp+size+4]
        op_codes.extend([0xb8])
        op_codes.extend((address).to_bytes(4, "little"))    #   mov     eax, address
        op_codes.extend([0xff, 0xd0])                       #   call    eax
        op_codes.extend([0xc3])                             #   ret
        return op_codes

    def get_size(self, argtypes):
        size = 0
        for argtype in args[1:]:
            sizeof_argtype = ctypes.sizeof(argtype)
            if sizeof_argtype >= 4:
                size += sizeof_argtype
            else:
                size += 4

        return size


class FASTCALL(THISCALL):

    def make_asm(self, argtypes, address):
        size = self.get_size(argtypes)
        op_codes = []
        op_codes.extend([0x8b, 0x4c, 0x24, 0x04])           #   mov     ecx, [esp+4]
        op_codes.extend([0x8b, 0x54, 0x24, 0x08])           #   mov     edx, [esp+8]
        for i in range(0, size, 4):
            op_codes.extend([0xff, 0x74, 0x24, size+8])     #   push	dword[esp+size+8]
        op_codes.extend([0xb8])
        op_codes.extend((address).to_bytes(4, "little"))    #   mov     eax, address
        op_codes.extend([0xff, 0xd0])                       #   call    eax
        op_codes.extend([0xc3])                             #   ret
        return op_codes

    def get_size(self, argtypes):
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


class FASTCALL_CALLER(FASTCALL):

    def make_asm(self, argtypes, address):
        size = self.get_size(argtypes)
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
        return op_codes


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def get_ctype_function(function, calling_convention=None, auto_dealloc=True):
    address = function.trampoline.address
    argtypes = get_ctype_argtypes(function.arguments)
    restype = get_ctype_from_data_type(function.return_type)

    if calling_convention is None:
        if function.convention != Convention.CUSTOM:
            calling_convention = get_ctype_calling_convention(
                function.convention)
        else:
            raise ValueError("Calling convention is not specified.")

    return calling_convention(address, argtypes, restype, auto_dealloc)

def get_ctype_calling_convention(calling_convention):
    if PLATFORM == "linux":
        return CDECL

    if calling_convention == Convention.CDECL:
        return CDECL
    elif calling_convention == Convention.STDCALL:
        return STDCALL
    elif calling_convention == Convention.THISCALL:
        return THISCALL
    elif calling_convention == Convention.FASTCALL:
        return FASTCALL
    else:
        raise ValueError("Given calling_convention is not supported.")

def get_ctype_argtypes(argtypes):
    ctype_argtypes = list()
    for data_type in argtypes:
        ctype_argtypes.append(
            get_ctype_from_data_type(data_type))
    return tuple(ctype_argtypes)

def get_ctype_from_data_type(data_type):
    if data_type == DataType.VOID:
        return None
    elif data_type == DataType.BOOL:
        return ctypes.c_bool
    elif data_type == DataType.CHAR:
        return ctypes.c_char
    elif data_type == DataType.UCHAR:
        return ctypes.c_ubyte
    elif data_type == DataType.SHORT:
        return ctypes.c_short
    elif data_type == DataType.USHORT:
        return ctypes.c_ushort
    elif data_type == DataType.INT:
        return ctypes.c_int
    elif data_type == DataType.UINT:
        return ctypes.c_uint
    elif data_type == DataType.LONG:
        return ctypes.c_long
    elif data_type == DataType.ULONG:
        return ctypes.c_ulong
    elif data_type == DataType.LONG_LONG:
        return ctypes.c_longlong
    elif data_type == DataType.ULONG_LONG:
        return ctypes.c_ulonglong
    elif data_type == DataType.FLOAT:
        return ctypes.c_float
    elif data_type == DataType.DOUBLE:
        return ctypes.c_double
    elif data_type == DataType.POINTER:
        return ctypes.c_void_p
    elif data_type == DataType.STRING:
        return ctypes.c_char_p
    else:
        raise ValueError("Given data_type is not supported.")

