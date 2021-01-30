# ../addons/source-python/packages/custom/memorytools/patcher.py

"""Provides a memory patching functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Ctypes
import ctypes
#   Weakref
from weakref import WeakValueDictionary

# Source.Python Imports
#   Core
from core import AutoUnload


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("Patcher",
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

        if isinstance(pointer, Pointer):
            address = pointer.address + offset
        elif isinstance(pointer, int):
            address = pointer + offset
        else:
            raise TypeError("pointer object({type}) is not Pointer.".format(type=type(pointer).__name__))

        for patched in self._patched.values():
            if (patched.address + patched.size - address) >= size:
                patched_address = hex(patched.address)
                patched_original = ''.join("\\x{:02x}".format(i) for i in patched.original)
                patched_op_codes = ''.join("\\x{:02x}".format(i) for i in patched.op_codes)
                raise ValueError(f"Patchers are overlapping!:\n    address '{patched_address}'\n    original '{patched_original}'\n    op_codes '{patched_op_codes}'")

        self.address = address
        self.size = size

        self.pointer = ctypes.c_void_p(address)
        self.original = bytes((ctypes.c_ubyte*size).from_address(address))
        self.op_codes = self.get_opcodes(op_codes, size)

        self.patched = False

        Pointer(address).unprotect(size)

        self._patched[id(self)] = self

    @classmethod
    def get_no_op(cls, size):
        max_no_op = len(cls.no_op_codes)
        quot = size // max_no_op
        rem = size % max_no_op
        return (cls.no_op_codes[-1]*quot if quot else b"")+(cls.no_op_codes[rem-1] if rem else b"")

    @classmethod
    def get_opcodes(cls, op_codes, size):
        if op_codes is not None:
            return op_codes+cls.get_no_op(size-len(op_codes))
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

