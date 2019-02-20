"""
Hossein Moein
February 8, 2019
Copyright (C) 2019-2020 Hossein Moein
Distributed under the BSD Software License (see file LICENSE)
"""

from datetime import datetime
from typing import Callable, TypeVar, Union


AllowedBaseTypes = Union[int, float, str, bool, datetime, None]
_DataItemBaseType = TypeVar('_DataItemBaseType', bound='DataItemBase')
_DataChangeCallback = Callable[[_DataItemBaseType, int, int], None]


class DataItemBase(object):
    """
    An abstract data item.
    DataItem's can carry/be any of the above "allowed types" with the following specs:
        1. A DataItem cannot change type with exceptions below. For example, once you create
           an integer DataItem, you cannot change it to an string or float.
        2. A non-null DataItem (i.e. a DataItem whose value is not None) can be set to null
           only by calling the set_to_null() method.
        3. A null DataItem (i.e. a DataItem whose value is None) can be set to a non-null value
           by calling the set_value() method.
        4. So, 2 and 3 explain the exceptions to 1.
    """

    def __init__(self: _DataItemBaseType) -> None:
        """Initialize."""
        super().__init__()
        # A callback to be called when value of this data item changes
        self._item_change_callback: _DataChangeCallback = None
        # The column index, in case this object is inside a container. Currently dependencies can
        # be triggered only on containers with one row. If we decide to have dependencies on many
        # rows (e.g. like Excel), we need to also store the row index here
        self._my_column_in_container: int = None
        # Current count of circles made around a circular dependency
        self._dependency_circle_count: int = 0

    def get_value(self: _DataItemBaseType) -> AllowedBaseTypes:
        """Abstract get value."""
        raise NotImplementedError('DataItemBase::get_value() is not implemented.')

    def get_string(self: _DataItemBaseType) -> str:
        """Get value as a string."""
        if self.is_null():
            # I am not really proud of this. But what are the alternatives?
            return '~~NULL~~'
        return str(self.get_value())

    def is_null(self: _DataItemBaseType) -> bool:
        """Is this null?"""
        return self.get_value() is None

    def is_container(self: _DataItemBaseType) -> bool:
        """Is this a container?"""
        return False

    def is_numeric(self: _DataItemBaseType) -> bool:
        """Is this a numeric?"""
        value: AllowedBaseTypes = self.get_value()
        return isinstance(value, float) or isinstance(value, int)

    def is_datetime(self: _DataItemBaseType) -> bool:
        """Is this a datetime?"""
        return isinstance(self.get_value(), datetime)

    def _touch(self: _DataItemBaseType) -> None:
        """Trigger dependency."""
        if self._item_change_callback is not None:
            self._item_change_callback(0, self._my_column_in_container)

    def __str__(self: _DataItemBaseType) -> str:
        """String representation."""
        return self.get_string()

    def __repr__(self: _DataItemBaseType) -> str:
        """String representation."""
        return self.__str__()

    def __eq__(self: _DataItemBaseType, other: _DataItemBaseType) -> bool:
        """== operator."""
        raise NotImplementedError('DataItemBase::__eq__() is not implemented.')

    def __ne__(self: _DataItemBaseType, other: _DataItemBaseType) -> bool:
        """!= operator."""
        return not self.__eq__(other)

    def __lt__(self: _DataItemBaseType, other: _DataItemBaseType) -> bool:
        """< operator."""
        raise NotImplementedError('DataItemBase::__lt__() is not implemented.')

    def __gt__(self: _DataItemBaseType, other: _DataItemBaseType) -> bool:
        """> operator."""
        raise NotImplementedError('DataItemBase::__gt__() is not implemented.')

    def __le__(self: _DataItemBaseType, other: _DataItemBaseType) -> bool:
        """<= operator."""
        return not self.__gt__(other)

    def __ge__(self: _DataItemBaseType, other: _DataItemBaseType) -> bool:
        """>= operator."""
        return not self.__lt__(other)

    def _set_to_null_hook(self: _DataItemBaseType) -> bool:
        """Set hook to be implemented by derived classes."""
        raise NotImplementedError('DataItemBase::_set_to_null_hook() is not implemented.')

    def _set_hook(self: _DataItemBaseType,
                  value: Union[_DataItemBaseType, AllowedBaseTypes]) -> bool:
        """Set hook to be implemented by derived classes."""
        raise NotImplementedError('DataItemBase::_set_hook() is not implemented.')

    def set_to_null(self: _DataItemBaseType) -> None:
        """This is the only way to set an existing non-null DataItem to null"""
        if self._set_to_null_hook():  # A true return means something was changed
            self._touch()  # Trigger the dependencies, if they are set up.

    def set_value(self: _DataItemBaseType,
                  value: Union[_DataItemBaseType, AllowedBaseTypes]) -> None:
        """Set value method."""
        if self._set_hook(value):  # A true return means something was changed
            self._touch()  # Trigger the dependencies, if they are set up.
