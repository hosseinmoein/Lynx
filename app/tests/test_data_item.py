"""
Hossein Moein
February 8, 2019
Copyright (C) 2019-2020 Hossein Moein
Distributed under the BSD Software License (see file LICENSE)
"""

from datetime import datetime
import unittest

from ..container_item import ContainerItem
from ..data_item import DataItem


class TestDataItems(unittest.TestCase):
    """Test all data items."""

    def test_data_item(self):
        """Test the data item."""
        int_item = DataItem(4)
        float_item = DataItem(45.67)
        float_item2 = DataItem(4.0)
        str_item = DataItem('test string')
        bool_item = DataItem(False)
        null_item = DataItem(None)

        self.assertTrue(float_item > int_item)
        self.assertTrue(float_item >= int_item)
        self.assertTrue(float_item > float_item2)
        self.assertFalse(null_item > int_item)
        self.assertFalse(int_item > null_item)
        self.assertEqual(int_item.get_value(), 4)
        self.assertEqual(float_item.get_value(), 45.67)
        self.assertEqual(str_item.get_value(), 'test string')
        self.assertFalse(bool_item.get_value())
        self.assertIsNone(null_item.get_value())
        self.assertFalse(bool_item.is_container())
        self.assertTrue(int_item == float_item2)
        self.assertFalse(int_item == float_item)

        with self.assertRaises(AttributeError):
            str_item.get(row=5, column='col_name')
        null_item._touch()
        float_item2.set_value(int_item.get_value())
        self.assertEqual(float_item2.get_value(), 4.0)
        int_item.set_value(11)
        float_item2.set_value(int_item)
        self.assertEqual(float_item2.get_value(), 11.0)
        int_item.set_value(-2)
        self.assertEqual(float_item2.get_value(), 11.0)

    def test_datetime(self):
        """Test the datetime data item."""
        datetime_item1 = DataItem(
            datetime(2019, month=2, day=6, hour=14, minute=47, second=40, microsecond=123456)
        )
        datetime_item2 = DataItem(datetime.now())

        self.assertEqual(datetime_item1.get_value().date().year, 2019)
        self.assertEqual(datetime_item1.get_value().minute, 47)
        self.assertTrue(datetime_item2 != datetime_item1)
        self.assertTrue(datetime_item2 > datetime_item1)

    def test_null_behavior(self):
        """Test null handling."""
        int_item = DataItem(4)
        str_item = DataItem('test string')
        null_item = DataItem(None)
        datetime_item = DataItem(datetime.now())

        with self.assertRaises(TypeError):
            int_item.set_value(None)
        with self.assertRaises(TypeError):
            int_item.set_value(null_item)
        self.assertEqual(int_item.get_value(), 4)
        str_item.set_to_null()
        self.assertTrue(str_item.get_value() is None)
        self.assertTrue(null_item.get_value() is None)
        null_item.set_value(34)
        self.assertEqual(null_item.get_value(), 34)
        null_item.set_to_null()
        self.assertTrue(null_item.get_value() is None)
        null_item.set_value('test string')
        self.assertEqual(null_item.get_value(), 'test string')
        self.assertFalse(datetime_item.get_value() is None)
        datetime_item.set_to_null()
        self.assertTrue(datetime_item.get_value() is None)
        datetime_item.set_value(datetime.now())
        self.assertFalse(datetime_item.get_value() is None)

    def test_container_item(self):
        """Test the container item."""
        self.maxDiff = 2048
        ci = ContainerItem()
        ci.add_float_column('float_column1', 45.5)
        ci.add_float_column('float_column2', None)
        ci.add_string_column('str_column', 'Alakazam')
        ci.add_integer_column('int_column', 34)
        ci.add_integer_column('int_column2', 5)
        ci.add_datetime_column('datetime_column', datetime(2019, 2, 23, 23, 30, 45, 965234))
        ci.add_null_column('might_be_null_column')
        ci.add_row('int_column', 50)
        ci.add_row('int_column', 51)
        ci.add_row('str_column', 'Bugs Bunny')
        ci.add_row('datetime_column', datetime(2019, 2, 21, 4, 50, 0, 230000))
        ci.add_row('might_be_null_column', 45)

        self.assertEqual(ci.number_of_columns(), 7)
        self.assertEqual(ci.number_of_rows('int_column'), 3)
        self.assertEqual(ci.number_of_rows('datetime_column'), 2)
        self.assertTrue(ci.is_container())

        ci_2 = ContainerItem()
        ci_2.set_value(ci)
        self.assertFalse(ci == ci_2)  # Because there are null columns
        self.assertTrue(ci != ci_2)  # Because there are null columns
        ci_2.add_container_column('container_column', ci)
        ci_2.get(column='int_column').set_value(-34)

        self.assertEqual(
            ci_2.get_string(),
            'float_column1: 45.5,\nfloat_column2: ~~NULL~~,\nstr_column: Alakazam,Bugs Bunny,\n'
            'int_column: -34,50,51,\nint_column2: 5,\ndatetime_column: 2019-02-23 23:30:45.965234,'
            '2019-02-21 04:50:00.230000,\nmight_be_null_column: ~~NULL~~,45,\ncontainer_column:  '
            '{\n    float_column1: 45.5,\n    float_column2: ~~NULL~~,\n    str_column: Alakazam,'
            'Bugs Bunny,\n    int_column: 34,50,51,\n    int_column2: 5,\n    datetime_column: '
            '2019-02-23 23:30:45.965234,2019-02-21 04:50:00.230000,\n    might_be_null_column: '
            '~~NULL~~,45,\n}\n\n')

        self.assertEqual(ci.get(column='int_column').get_value(), 34)
        self.assertEqual(ci_2.get(column='int_column').get_value(), -34)
        self.assertEqual(
            ci_2.get(column='container_column').get(column='int_column').get_value(), 34
        )
        self.assertEqual(ci.get(row=2, column='int_column').get_value(), 51)
        self.assertEqual(ci_2.get(row=2, column='int_column').get_value(), 51)
        self.assertTrue(ci_2.contains('float_column2'))

        with self.assertRaises(RuntimeError):
            ci_2.add_row('str_column', False)

        self.assertEqual(ci.number_of_columns(), 7)
        self.assertEqual(ci.column_index('str_column'), 2)
        self.assertEqual(ci.column_index('int_column2'), 4)
        self.assertEqual(ci.column_index('int_column'), 3)
        self.assertEqual(ci.get(column='int_column2').get_value(), 5)
        self.assertTrue(ci.contains('int_column'))
        ci.remove_column('int_column')
        self.assertEqual(ci.number_of_columns(), 6)
        self.assertEqual(ci.column_index('str_column'), 2)
        self.assertEqual(ci.column_index('int_column2'), 3)
        self.assertEqual(ci.get(column='int_column2').get_value(), 5)
        self.assertFalse(ci.contains('int_column'))
        with self.assertRaises(IndexError):
            ci.remove_column('xxxx')

        ci.add_integer_column('int_column', None)
        ci.add_row('int_column', 50)
        ci.add_row('int_column', 51)
        ci.add_row('int_column', None)
        self.assertEqual(ci.number_of_rows('int_column'), 4)
        self.assertIsNone(ci.get(column='int_column', row=0).get_value())
        self.assertEqual(ci.get(column='int_column', row=1).get_value(), 50)
        self.assertEqual(ci.get(column='int_column', row=2).get_value(), 51)
        self.assertIsNone(ci.get(column='int_column', row=3).get_value())
        ci.remove_row('int_column', 1)
        self.assertEqual(ci.number_of_rows('int_column'), 3)
        self.assertIsNone(ci.get(column='int_column', row=0).get_value())
        self.assertEqual(ci.get(column='int_column', row=1).get_value(), 51)
        ci.remove_row('int_column', 0)
        self.assertEqual(ci.number_of_rows('int_column'), 2)
        self.assertEqual(ci.get(column='int_column').get_value(), 51)
        ci.remove_row('int_column', 1)
        with self.assertRaises(IndexError):
            ci.remove_row('int_column', 1)
        ci.remove_row('int_column', 0)
        self.assertFalse(ci.contains('int_column'))
