# ../addons/source-python/packages/custom/memorytools/patcher.py

"""Provides a memory patching functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Collections
from collections.abc import MutableMapping
#   Ctypes
from ctypes import c_ubyte
from ctypes import c_void_p
from ctypes import memmove
#   Weakref
from weakref import WeakValueDictionary

# Source.Python Imports
#   Core
from core import WeakAutoUnload
#   Memory
from memory import Pointer

# Memory Tools Imports
#   Memory Tools
from memorytools import get_jmp_bytes


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("make_jmp",
           "Patcher",
           "Patchers",
           )


# =============================================================================
# >> CLASSES
# =============================================================================
class Patcher(WeakAutoUnload):
    _patchers = dict()

    no_op_codes = [
        b"\x90",
        b"\x66\x90",
        b"\x0f\x1f\x00",
        b"\x0f\x1f\x40\x00",
        b"\x0f\x1f\x44\x00\x00",
        b"\x66\x0f\x1f\x44\x00\x00",
        b"\x0f\x1f\x80\x00\x00\x00\x00",
        b"\x0f\x1f\x84\x00\x00\x00\x00\x00",
        b"\x66\x0f\x1f\x84\x00\x00\x00\x00\x00",
    ]

    def __init__(self, pointer, size, op_codes=None, base_op_codes=None):
        """Initialize the patcher.

        :param Pointer/int pointer:
            The pointer or memory address to patch the memory.
        :param int size:
            The size of the memory to be patched.
        :param bytes op_codes:
            A specific op-codes to patch the memory.
        :param bytes base_op_codes:
            Base op-codes used for verification to prevent crashes
            when binary has been changed.
        :raise TypeError:
            Raised if ``pointer`` is not Pointer or int.
        :raise ValueError:
            Raised if the patcher is overlapping with another patcher's
            memory space or ``base_op_codes`` does not match the original
            op-codes or ``op_codes`` and ``base_op_codes`` exceed ``size``.
        """
        self._patchable = False

        if not isinstance(pointer, (Pointer, int)):
            raise TypeError("pointer type is not Pointer/int: {type}".format(type=repr(type(pointer))))

        if op_codes is not None and len(op_codes) > size:
            op_codes = ' '.join("{:02X}".format(i) for i in op_codes)
            raise ValueError(f"Length of op_codes exceeds the patch size:\n    size '{size}'\n    op_codes '{op_codes}'")

        if base_op_codes is not None and len(base_op_codes) > size:
            base_op_codes = ' '.join("{:02X}".format(i) for i in base_op_codes)
            raise ValueError(f"Length of base_op_codes exceeds the patch size:\n    size '{size}'\n    base_op_codes '{base_op_codes}'")

        address = int(pointer)

        for patcher in self._patchers.values():
            if (address <= patcher.address):
                small_address = address + size
                large_address = patcher.address
            else:
                small_address = patcher.address + patcher.size
                large_address = address

            if small_address > large_address:
                patcher_address = hex(patcher.address)
                patcher_original = ' '.join("{:02X}".format(i) for i in patcher.original)
                patcher_op_codes = ' '.join("{:02X}".format(i) for i in patcher.op_codes)
                raise ValueError(f"Patcher's memory space is overlapping:\n    address '{patcher_address}'\n    original '{patcher_original}'\n    op_codes '{patcher_op_codes}'")

        original = bytes((c_ubyte*size).from_address(address))

        if base_op_codes is not None:
            original_op_codes = original[:len(base_op_codes)]
            for base_byte, original_byte, in zip(base_op_codes, original_op_codes):
                if base_byte != 0x2A and base_byte != original_byte:
                    original_op_codes = ' '.join("{:02X}".format(i) for i in original_op_codes)
                    base_op_codes = ' '.join("{:02X}".format(i) for i in base_op_codes).replace("2A", "??")
                    raise ValueError(f"Original op-codes does not match base_op_codes:\n    original '{original_op_codes}'\n    base     '{base_op_codes}'")

        Pointer(address).unprotect(size)

        self.address = address
        self.size = size
        self.pointer = c_void_p(address)
        self.original = original
        self.op_codes = self.get_op_codes(op_codes, size)

        self.patched = False
        self._patchable = True

        self._patchers[id(self)] = self

    @classmethod
    def get_no_op(cls, size):
        if size <= 0:
            return b""
        max_no_op = len(cls.no_op_codes)
        quot = size // max_no_op
        rem = size % max_no_op
        return (cls.no_op_codes[-1]*quot if quot else b"")+(cls.no_op_codes[rem-1] if rem else b"")

    @classmethod
    def get_op_codes(cls, op_codes, size):
        if op_codes is not None:
            return op_codes[:size]+cls.get_no_op(size-len(op_codes))
        else:
            return cls.get_no_op(size)

    def patch(self):
        if not self.patched and self._patchable:
            memmove(self.pointer, self.op_codes, self.size)
            self.patched = True

    def reset(self):
        if self.patched and self._patchable:
            memmove(self.pointer, self.original, self.size)
            self.patched = False

    def set(self, state):
        if state:
            self.patch()
        else:
            self.reset()

    def toggle(self):
        if not self.patched:
            self.patch()
        else:
            self.reset()

    def _unload_instance(self):
        if self._patchable:
            self.reset()
            self._patchable = False

            del self._patchers[id(self)]


class Patchers(MutableMapping):
    def __init__(self, *args, **kwargs):
        self._patchers = dict()
        self.patched = False
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        return self._patchers.__getitem__(key)

    def __setitem__(self, key, value):
        if not isinstance(value, Patcher):
            raise TypeError("Object type is not Patcher: {type}".format(type=repr(type(value))))
        self._patchers.__setitem__(key, value)

        setattr(self, key, value)

    def __delitem__(self, key):
        self._patchers.__delitem__(key)

    def __iter__(self):
        return self._patchers.__iter__()

    def __len__(self):
        return self._patchers.__len__()

    def patch(self):
        for patcher in self._patchers.values():
            patcher.patch()
        self.patched = True

    def reset(self):
        for patcher in self._patchers.values():
            patcher.reset()
        self.patched = False

    def set(self, state):
        if state:
            self.patch()
        else:
            self.reset()

    def toggle(self):
        for patcher in self._patchers.values():
            patcher.toggle()

    def toggle_all(self):
        if not self.patched:
            self.patch()
        else:
            self.reset()


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def make_jmp(base, dest, short=True):
    jmp_bytes = get_jmp_bytes(base, dest, short)
    return Patcher(base, len(jmp_bytes), jmp_bytes)

