"""
Hossein Moein
February 8, 2019
Copyright (C) 2019-2020 Hossein Moein
Distributed under the BSD Software License (see file LICENSE)
"""

import copy
from datetime import datetime
from typing import Dict, List, Tuple, TypeVar, Union

from .data_item_base import AllowedBaseTypes, DataItemBase
from .data_item import DataItem


_ContainerItemType = TypeVar('_ContainerItemType', bound='ContainerItem')


class ContainerItem(DataItemBase):
    """
    A container item that is a tabular container of data items.
        1. ContainerItem represents a tabular container of rows and columns containing DataItem's,
           accessible by column names or indices and row indices.
        2. Because of this recursive definition, a ContainerItem column could be another
           ContainerItem. So, ContainerItem is not necessarily tabular. It could take any arbitrary
           shape.
        3. All rows in a given column of ContainerItem are of the same DataItem type. For example,
           all rows of a given column are all either a DatItem of integer type or float type, etc.
    """

    def __init__(self: _ContainerItemType) -> None:
        """Initialize."""
        super().__init__()
        # Vector of column names and types
        self._column_names_and_types: List[Tuple[str, type]] = []
        self._column_data: List[List[DataItemBase]] = []  # Vector of vector of DataItems
        self._names_dict: Dict[str, int] = {}  # Hash table of column names -> column index

    @classmethod
    def _string_format(cls, container: _ContainerItemType, offset: str = '') -> str:
        """Class method to format the container nicely."""
        result: str = ''
        for name_and_type in container._column_names_and_types:
            result += f'{offset}{name_and_type[0]}: '
            data_idx: int = container._names_dict.get(name_and_type[0], -1)
            for data_item in container._column_data[data_idx]:
                if isinstance(data_item, ContainerItem):
                    result += ' {\n'
                    result += ContainerItem._string_format(data_item, offset + '    ')
                    result += '}'
                else:
                    result += f'{data_item.get_string()},'
            result += '\n'
        return result

    def get_value(self: _ContainerItemType) -> AllowedBaseTypes:
        """get_value() for containers."""
        return ContainerItem._string_format(self)

    def is_container(self: _ContainerItemType) -> bool:
        """This is a container."""
        return True

    def __eq__(self: _ContainerItemType, other: _ContainerItemType) -> bool:
        """Equal operator for containers."""
        if not isinstance(other, ContainerItem):
            raise TypeError(
                'ContainerItem::__eq__(): Container item could only be compared '
                'with another container item'
            )
        return (self._column_data == other._column_data and
                self._column_names_and_types == other._column_names_and_types)

    def _set_value_hook(
            self: _ContainerItemType, value: Union[DataItemBase, AllowedBaseTypes]
    ) -> bool:
        """This is called by the parent set method."""
        if not isinstance(value, ContainerItem):
            raise TypeError(
                'ContainerItem::_set_value_hook(): Container item could only be assigned '
                'with another container item'
            )
        if self == value:
            return False
        # We don't want to copy the meta-data in DataItemBase
        self._column_names_and_types = copy.deepcopy(value._column_names_and_types)
        self._column_data = copy.deepcopy(value._column_data)
        self._names_dict = copy.deepcopy(value._names_dict)
        return True

    # Container item specific interface

    def number_of_columns(self: _ContainerItemType) -> int:
        """Get the number of columns."""
        return len(self._column_names_and_types)

    def number_of_rows(self: _ContainerItemType, column: Union[int, str]) -> int:
        """Get the number of rows for the given column"""
        col_index = self._names_dict.get(column, -1) if type(column) is str else column
        if col_index < 0:
            raise IndexError(f'ContainerItem::number_of_rows(): column {column} does not exist')
        return len(self._column_data[col_index])

    def get(self: _ContainerItemType, row: int = 0, column: Union[int, str] = 0) -> DataItemBase:
        """Get data from container for the given row and column."""
        column_num = self._names_dict.get(column) if type(column) is str else column
        if column_num is None or column_num < 0 or column_num >= len(self._column_data):
            raise IndexError(f'ContainerItem::get(): column {column} does not exist')
        if row < 0 or row >= len(self._column_data[column_num]):
            raise IndexError(f'ContainerItem::get(): row {row} does not exist for column {column}')
        return self._column_data[column_num][row]

    def column_name(self: _ContainerItemType, column: int) -> str:
        """Return column name given index."""
        return self._column_names_and_types[column][0]

    def column_index(self: _ContainerItemType, column: str) -> int:
        """Return column index given name."""
        col_index = self._names_dict.get(column, -1)
        if col_index < 0:
            raise IndexError(f'ContainerItem::column_index(): column {column} does not exist')
        return col_index

    def contains(self: _ContainerItemType, column: str) -> bool:
        """Does it contain the column of the given name?"""
        return bool(self._names_dict.get(column, False))

    def _add_column(
        self: _ContainerItemType,
        name: str,
        value: Union[AllowedBaseTypes, DataItemBase],
        column_type: type,
    ) -> DataItemBase:
        """Private method to add a new column."""
        if self._names_dict.get(name, False):
            raise RuntimeError(f'ContainerItem::_add_column(): column {name} already exists')
        self._column_names_and_types.append((name, column_type))
        col_index = len(self._column_names_and_types) - 1
        self._names_dict[name] = col_index
        data_item: Union[AllowedBaseTypes, DataItemBase] = value  # If this is a ContainerItem
        if type(value) is datetime or value is None:
            data_item = DataItem(value)
        elif not isinstance(value, ContainerItem):
            data_item = DataItem(column_type(value))
        data_item._my_column_in_container = col_index  # Sneaking a private member access!
        self._column_data.append([data_item])
        return data_item

    def remove_column(self: _ContainerItemType, column: Union[int, str]) -> None:
        """Remove the given column."""
        column_num = self._names_dict.get(column) if type(column) is str else column
        if column_num is None or column_num < 0 or column_num >= len(self._column_data):
            raise IndexError(f'ContainerItem::remove_column(): column {column} does not exist')
        del self._column_names_and_types[column_num]
        del self._column_data[column_num]
        self._names_dict = {nt[0]: idx for idx, nt in enumerate(self._column_names_and_types)}

    def add_integer_column(
        self: _ContainerItemType, name: str, value: Union[int, None]
    ) -> DataItemBase:
        """Add an integer column."""
        return self._add_column(name, value, int)

    def add_float_column(
        self: _ContainerItemType, name: str, value: Union[float, None]
    ) -> DataItemBase:
        """Add a float column."""
        return self._add_column(name, value, float)

    def add_string_column(
        self: _ContainerItemType, name: str, value: Union[str, None]
    ) -> DataItemBase:
        """Add a string column."""
        return self._add_column(name, value, str)

    def add_bool_column(
            self: _ContainerItemType, name: str, value: Union[bool, None]
    ) -> DataItemBase:
        """Add a boolean column."""
        return self._add_column(name, value, bool)

    def add_datetime_column(
        self: _ContainerItemType, name: str, value: Union[datetime, None]
    ) -> DataItemBase:
        """Add a datetime column."""
        return self._add_column(name, value, datetime)

    def add_null_column(self: _ContainerItemType, name: str) -> DataItemBase:
        """Add a null column."""
        return self._add_column(name, None, type(None))

    def add_container_column(
        self: _ContainerItemType, name: str, value: _ContainerItemType
    ) -> DataItemBase:
        """Add a container column."""
        return self._add_column(name, value, ContainerItem)

    def add_row(
        self: _ContainerItemType,
        column: Union[str, int],
        value: Union[AllowedBaseTypes, _ContainerItemType],
    ) -> DataItemBase:
        """Add a row to the given column."""
        data_index = self._names_dict.get(column) if type(column) is str else column
        if data_index is None or data_index < 0 or data_index >= len(self._column_data):
            raise RuntimeError(f'ContainerItem::add_row(): column {str(column)} does not exist')

        # Special handling for null columns: if a column was originally added as null, allow it to
        # change type. After that this column could only have rows of null or this type.
        if (self._column_names_and_types[data_index][1] is type(None) and
                value is not None):   # noqa: E721
            name_and_type = (self._column_names_and_types[data_index][0], type(value))
            self._column_names_and_types[data_index] = name_and_type

        if self._column_names_and_types[data_index][1] is not type(value) and value is not None:
            raise RuntimeError(
                f'ContainerItem::add_row(): Type mismatch between column {str(column)}, '
                f'value {str(value)}'
            )

        data_item = DataItem(value) if not isinstance(value, ContainerItem) else value
        self._column_data[data_index].append(data_item)
        return data_item

    def remove_row(self: _ContainerItemType, column: Union[str, int], row_index: int) -> None:
        """Remove the row for the given column."""
        column_num = self._names_dict.get(column) if type(column) is str else column
        if column_num is None or column_num < 0 or column_num >= len(self._column_data):
            raise IndexError(f'ContainerItem::remove_row(): column {column} does not exist')
        row_len = len(self._column_data[column_num])
        if row_len <= row_index:
            raise IndexError(f'ContainerItem::remove_row(): '
                             f'row {row_index} does not exist for column {column}')
        if row_len == 1:
            self.remove_column(column_num)
        else:
            del self._column_data[column_num][row_index]

