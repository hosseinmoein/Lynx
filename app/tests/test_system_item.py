"""
Hossein Moein
February 8, 2019
Copyright (C) 2019-2020 Hossein Moein
Distributed under the BSD Software License (see file LICENSE)
"""

import unittest

from ..system_item import DependencyResult, SystemItem


SOMETHING_TO_CHANGE: int = 10


class USTreasuryBond(SystemItem):
    """A crude simulation of a US treasury bond."""

    def __init__(self) -> None:
        """Initialize."""
        super().__init__()
        self.turn_dependency_off()
        self.add_float_column('price', 0)
        self.add_float_column('yield', 0)
        self.add_float_column('dv01', 0)
        self.add_integer_column('expiration', 0)
        self.wire()

    def price_to_yield(self, price_col: int, yield_col: int) -> DependencyResult:
        """Price to yield calculation."""
        price = self.get(column=price_col).get_value()
        yield_val = price / 100.0 * 1.5
        self.get(column=yield_col).set_value(yield_val)
        return DependencyResult.SUCCESS

    def yield_to_price(self, yield_col: int, price_col: int) -> DependencyResult:
        """Yield to price calculation."""
        yield_val = self.get(column=yield_col).get_value()
        price = yield_val / 1.5 * 100.0
        self.get(column=price_col).set_value(price)
        return DependencyResult.SUCCESS

    def price_to_dv01(self, price_col: int, dv01_col: int) -> DependencyResult:
        """Yield to price calculation."""
        price = self.get(column=price_col).get_value()
        self.get(column=dv01_col).set_value(price / 100.0)
        return DependencyResult.SUCCESS

    def dv01_action(self, dv01_col: int) -> DependencyResult:
        """Action taken when dv01 changes"""
        global SOMETHING_TO_CHANGE
        SOMETHING_TO_CHANGE *= 2
        return DependencyResult.SUCCESS

    def wire(self) -> None:
        """Setup the dependencies."""
        self.add_dependency(
            self.column_index('price'), self.column_index('yield'), self.price_to_yield
        )
        self.add_dependency(
            self.column_index('yield'), self.column_index('price'), self.yield_to_price
        )
        self.add_dependency('price', self.column_index('dv01'), self.price_to_dv01)
        self.add_action('dv01', self.dv01_action)


class TestSystemItem(unittest.TestCase):
    """Test SystemItem."""

    def test_system_item(self):
        """Test the system item."""
        us_bond = USTreasuryBond()
        us_bond.get(column='price').set_value(120.0)
        us_bond.get(column='yield').set_value(1.5)  # We are in an inconsistent state now
        us_bond.get(column='dv01').set_value(100.0)  # We are in an inconsistent state now
        self.assertEqual(us_bond.get(column='price').get_value(), 120.0)
        self.assertEqual(us_bond.get(column='yield').get_value(), 1.5)
        self.assertEqual(us_bond.get(column='dv01').get_value(), 100.0)

        us_bond.turn_dependency_on()
        # The circular price <-> yield dependency is being tested
        us_bond.get(column='price').set_value(100.5)
        self.assertEqual(us_bond.get(column='price').get_value(), 100.5)
        self.assertAlmostEqual(us_bond.get(column='yield').get_value(), 1.50749999)
        self.assertAlmostEqual(us_bond.get(column='dv01').get_value(), 1.005)
        self.assertEqual(SOMETHING_TO_CHANGE, 20)

        us_bond.get(column='expiration').set_value(20251230)
        self.assertEqual(us_bond.get(column='price').get_value(), 100.5)
        self.assertAlmostEqual(us_bond.get(column='yield').get_value(), 1.50749999)
        self.assertAlmostEqual(us_bond.get(column='dv01').get_value(), 1.005)
        self.assertEqual(SOMETHING_TO_CHANGE, 20)

        # The circular price <-> yield dependency is being tested
        us_bond.get(column='yield').set_value(1.55)
        self.assertAlmostEqual(us_bond.get(column='price').get_value(), 103.3333333)
        self.assertAlmostEqual(us_bond.get(column='yield').get_value(), 1.55)
        self.assertAlmostEqual(us_bond.get(column='dv01').get_value(), 1.0333333)
        self.assertEqual(SOMETHING_TO_CHANGE, 40)
