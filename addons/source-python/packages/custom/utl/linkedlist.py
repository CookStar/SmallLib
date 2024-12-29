# ../addons/source-python/packages/custom/utl/linkedlist.py

"""Provides UtlLinkedList based functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Memory
from memory import TYPE_SIZES
from memory import get_size
from memory import make_object
from memory.helpers import Type
#   Paths
from paths import CUSTOM_DATA_PATH

# Utl Imports
#   Manager
from utl.manager import type_manager
#   Memory
from utl.memory import UtlMemory


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ('UtlLinkedList',
           )


# =============================================================================
# >> UtlLinkedList
# =============================================================================
_UtlLinkedList = type_manager.create_type_from_file(
    '_UtlLinkedList',
    CUSTOM_DATA_PATH / 'utl' / 'linkedlist' / 'CUtlLinkedList.ini',
    (UtlMemory,),
)

class UtlLinkedList(_UtlLinkedList, metaclass=type_manager):
    _is_ptr = False
    _type = Type.POINTER

    _is_native = None
    _type_size = None

    INVALID_INDEX = -1

    def __new__ (cls, *args, **kwargs):
        if cls._is_native is None or cls._type_size is None:
            if isinstance(cls._type, str):
                type_size = TYPE_SIZES.get(cls._type.upper(), None)
                if type_size is not None:
                    cls._is_native = True
            else:
                type_size = get_size(cls._type)
                cls._is_native = False

            if cls._is_ptr:
                type_size = TYPE_SIZES[Type.POINTER.upper()]

            if cls._type_size is None:
                if type_size is None:
                    raise ValueError('Unable to get type size.')

                cls._type_size = type_size

            if cls._is_native is None:
                raise ValueError('Unable to get type.')

        return super().__new__(cls, *args, **kwargs)

    def __contains__(self, item):
        is_ptr = bool(self._is_ptr and not self._is_native)
        if is_ptr:
            item_ptr = get_object_pointer(item)

        for element in self:
            if is_ptr:
                element_ptr = get_object_pointer(element)
                if element_ptr == item_ptr:
                    return True

            if element == item:
                return True

        return False

    def __iter__(self):
        iter = self.head
        base = self.base
        while True:
            if iter == self.INVALID_INDEX:
                break

            yield self.convert(base)

            iter = base.get_short(self._type_size + 0x02)
            base += self._type_size + 0x04

    def __len__(self):
        return self.element_count

    @classmethod
    def convert(cls, ptr):
        if cls._is_ptr:
            ptr = ptr.get_pointer()

        if cls._is_native:
            return getattr(ptr, 'get_' + cls._type)()
        else:
            return make_object(cls._type, ptr)

