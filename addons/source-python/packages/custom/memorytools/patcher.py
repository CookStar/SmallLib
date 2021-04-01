# ../addons/source-python/packages/custom/memorytools/patcher.py

"""Provides a memory patching functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Collections
from collections.abc import MutableMapping
#   Ctypes
import ctypes
#   Weakref
from weakref import WeakValueDictionary

# Source.Python Imports
#   Core
from core import AutoUnload
#   Memory
from memory import Pointer


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("Patcher",
           "Patchers",
           )


# =============================================================================
# >> CLASSES
# =============================================================================
class Patcher(AutoUnload):
    _patched = WeakValueDictionary()

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

    def __init__(self, pointer, size, op_codes=None):
        """Initialize the downloader.

        :param Pointer/int pointer:
            The pointer or memory address to patch the memory.
        :param int size:
            The size of the memory to be patched.
        :param bytes op_codes:
            A specific op-codes to patch the memory.
        :raise TypeError:
            Raised if ``pointer`` is not Pointer or int.
        :raise ValueError:
            Raised if the patcher is overlapping with
            another patcher's memory space.
        """

        if not isinstance(pointer, (Pointer, int)):
            raise TypeError("pointer type is not Pointer/int: {type}".format(type=repr(type(pointer))))

        self.address = int(pointer)
        self.size = size

        for patched in self._patched.values():
            if (self.address <= patched.address):
                small_address = self.address + self.size
                large_address = patched.address
            else:
                small_address = patched.address + patched.size
                large_address = self.address

            if small_address > large_address:
                patched_address = hex(patched.address)
                patched_original = ' '.join("{:02X}".format(i) for i in patched.original)
                patched_op_codes = ' '.join("{:02X}".format(i) for i in patched.op_codes)
                raise ValueError(f"Patcher's memory space is overlapping!:\n    address '{patched_address}'\n    original '{patched_original}'\n    op_codes '{patched_op_codes}'")

        Pointer(self.address).unprotect(self.size)

        self.pointer = ctypes.c_void_p(self.address)
        self.original = bytes((ctypes.c_ubyte*self.size).from_address(self.address))
        self.op_codes = self.get_opcodes(op_codes, self.size)

        self.patched = False

        self._patched[id(self)] = self

    @classmethod
    def get_no_op(cls, size):
        if size <= 0:
            return b""
        max_no_op = len(cls.no_op_codes)
        quot = size // max_no_op
        rem = size % max_no_op
        return (cls.no_op_codes[-1]*quot if quot else b"")+(cls.no_op_codes[rem-1] if rem else b"")

    @classmethod
    def get_opcodes(cls, op_codes, size):
        if op_codes is not None:
            return op_codes[:size]+cls.get_no_op(size-len(op_codes))
        else:
            return cls.get_no_op(size)

    def patch(self):
        ctypes.memmove(self.pointer, self.op_codes, self.size)
        self.patched = True

    def reset(self):
        ctypes.memmove(self.pointer, self.original, self.size)
        self.patched = False

    def toggle(self):
        if not self.patched:
            self.patch()
        else:
            self.reset()

    def _unload_instance(self):
        if self.patched:
            self.reset()

        del self._patched[id(self)]


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

    def toggle(self):
        for patcher in self._patchers.values():
            patcher.toggle()

    def toggle_all(self):
        if not self.patched:
            self.patch()
        else:
            self.reset()

