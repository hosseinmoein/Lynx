"""
Hossein Moein
February 8, 2019
Copyright (C) 2019-2020 Hossein Moein
Distributed under the BSD Software License (see file LICENSE)
"""

from enum import Enum
from typing import Callable, List, NewType, TypeVar, Union

from .container_item import ContainerItem
from .data_item_base import AllowedBaseTypes, DataItemBase


_SystemItemType = TypeVar('_SystemItemType', bound='SystemItem')


class DependencyResult(Enum):
    """Result of a dependency callback execution"""

    SUCCESS = 0
    FAILURE = 1
    NO_CHANGE = 2


_DataChangeDependencyCallback = NewType(
    '_DataChangeDependencyCallback', Callable[[_SystemItemType, int, int], DependencyResult]
)
_DataChangeActionCallback = NewType(
    '_DataChangeActionCallback', Callable[[_SystemItemType, int], DependencyResult]
)


class _DependencyItem(object):
    """An object to represent a dependency in SystemItem."""

    def __init__(self):
        """Initialize."""
        super().__init__()
        # The column that needs to be changed because of independent column change.
        # We do not need to store the independent column, since it would be the index in the list
        # of dependencies.
        self.dependent_column: int = None
        # The callback for dependency or action
        self.callback: Union[_DataChangeActionCallback, _DataChangeDependencyCallback] = None


class SystemItem(ContainerItem):
    """
    A system item that implements a dependency graph in a container item.
        1. A dependency specifies a relationship between an independent column (i.e. changed) and
           a dependent column (i.e. should to change as a result).
        2. An action specifies a reaction to a just-changed independent column.
    A system item allows many dependencies and many actions per column. Circular dependencies
    are allowed and handled properly, by going around the circle the set number of times.
    Currently, system item allows only one row in the container
    """

    def __init__(self: _SystemItemType) -> None:
        """Initialize."""
        super().__init__()
        # The vector of dependencies/actions per column
        self._dependency_vector: List[List[_DependencyItem]] = []
        self._dependency_on: bool = True  # Is dependency engine on?
        # Max number of times to go around a circular dependency before stopping
        self._dependency_circle_max: int = 1

    def get_value(self: _SystemItemType) -> AllowedBaseTypes:
        """get_value() for system item."""
        result = ''
        for name_and_type in self._column_names_and_types:
            result += f'{name_and_type[0]}: '
            data_idx = self._names_dict.get(name_and_type[0])
            for data_item in self._column_data[data_idx]:
                result += f'{data_item.get_string()},'
                if (len(self._dependency_vector[data_idx]) > 0 and
                        self._dependency_vector[data_idx][0].callback is not None):
                    result += ' -> '
                    for dep in self._dependency_vector[data_idx]:
                        result += f'{dep.callback.__name__},'
            result += '\n'
        return result

    def _dependency_engine(self: _SystemItemType, row: int, independent_column: int) -> None:
        """The dependency loop where things happen."""
        if self._dependency_on:
            for dep in self._dependency_vector[independent_column]:
                if dep.callback is None:  # Unfortunate side-affect of how _add_column works
                    break
                if dep.dependent_column is None:  # This is an action
                    dep.callback(independent_column)
                # This is a dependency, so we execute only if we are within the set
                # number around the circle.
                elif (self.get(column=dep.dependent_column)._dependency_circle_count <
                      self._dependency_circle_max):
                    # Increase the number of times we passed this item
                    self.get(column=independent_column)._dependency_circle_count += 1
                    dep.callback(independent_column, dep.dependent_column)
                    # Decrease the number of times we passed this item
                    self.get(column=independent_column)._dependency_circle_count -= 1
            else:  # we did not break, so there was a dependency
                # In case this system item itself is part of another system item dependency
                self._touch()

    def __eq__(self: _SystemItemType, other: DataItemBase) -> bool:
        """Equal operator for system item."""
        if not isinstance(other, SystemItem):
            raise TypeError(
                'SystemItem::__eq__(): System item could only be compared '
                'with another system container item'
            )

        parent_result = super().__eq__(other)
        if parent_result is False:
            return parent_result
        return self._dependency_vector == other._dependency_vector

    def _add_column(
        self: _SystemItemType,
        name: str,
        value: Union[AllowedBaseTypes, ContainerItem],
        column_type: type,
    ) -> DataItemBase:
        """Private method to add a new column."""
        new_column: DataItemBase = super()._add_column(name, value, column_type)

        new_column._item_change_callback = self._dependency_engine
        dep_item = _DependencyItem()
        self._dependency_vector.append([dep_item])
        return new_column

    def remove_column(self: _SystemItemType, column: Union[int, str]) -> None:
        raise NotImplementedError('SystemItem::remove_column(): Currently this is not implemented')

    def add_row(
        self: _SystemItemType,
        column: Union[str, int],
        value: Union[AllowedBaseTypes, ContainerItem],
    ) -> DataItemBase:
        """Add a row to the given column."""
        raise NotImplementedError('SystemItem::add_row(): You cannot add rows to a system item')

    def remove_row(self: _SystemItemType, column: Union[str, int], row_index: int) -> None:
        """Remove the row for the given column."""
        raise NotImplementedError('SystemItem::remove_row(): You cannot add rows to a system item')

    def add_dependency(
        self: _SystemItemType,
        independent_column: Union[int, str],
        dependent_column: Union[int, str],
        callback: _DataChangeDependencyCallback,
    ) -> None:
        """Add a dependency callback for the given columns"""
        indep_col_idx = (
            self.column_index(independent_column)
            if isinstance(independent_column, str)
            else independent_column
        )
        dep_col_idx = (
            self.column_index(dependent_column)
            if isinstance(dependent_column, str)
            else dependent_column
        )
        dep_item = _DependencyItem()
        dep_item.dependent_column = dep_col_idx
        dep_item.callback = callback

        # Is this the first dependency being added for this column?
        if self._dependency_vector[indep_col_idx][0].callback is None:
            self._dependency_vector[indep_col_idx][0] = dep_item
        else:  # append another dependency for the independent column
            self._dependency_vector[indep_col_idx].append(dep_item)

    def add_action(
        self: _SystemItemType,
        independent_column: Union[int, str],
        callback: _DataChangeActionCallback,
    ) -> None:
        """Add an action callback for the given columns"""
        indep_col_idx = (
            self.column_index(independent_column)
            if isinstance(independent_column, str)
            else independent_column
        )
        dep_item = _DependencyItem()
        dep_item.callback = callback

        # Is this the first action being added for this column?
        if self._dependency_vector[indep_col_idx][0].callback is None:
            self._dependency_vector[indep_col_idx][0] = dep_item
        else:  # append another action for the independent column
            self._dependency_vector[indep_col_idx].append(dep_item)

    def is_dependency_on(self: _SystemItemType) -> bool:
        """Is the dependency engine on?"""
        return self._dependency_on

    def turn_dependency_on(self: _SystemItemType) -> None:
        """Turn on the dependency engine."""
        self._dependency_on = True

    def turn_dependency_off(self: _SystemItemType) -> None:
        """Turn off the dependency engine."""
        self._dependency_on = False

    def set_dependency_circle_max(self: _SystemItemType, max_count: int) -> None:
        """Set max number of times to go around a circular dependency before stopping."""
        self._dependency_circle_max = max_count
