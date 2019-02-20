"""
Hossein Moein
February 8, 2019
Copyright (C) 2019-2020 Hossein Moein
Distributed under the BSD Software License (see file LICENSE)
"""

from datetime import datetime
import unittest

from ..system_item import DependencyResult, SystemItem


SOMETHING_TO_CHANGE: int = 10


class USTreasuryBond(SystemItem):
    """A crude simulation of a US treasury bond."""

    def __init__(self) -> None:
        """Initialize."""
        super().__init__()
        self.turn_dependency_off()
        self.add_float_column('price', None)
        self.add_float_column('yield', 0)
        self.add_float_column('yield2', 0)
        self.add_float_column('yield3', 0)
        self.add_float_column('yield4', 0)
        self.add_float_column('dv01', 0)
        self.add_datetime_column('expiration', None)
        self.wire()

    def price_to_yield(self, price_col: int, yield_col: int) -> DependencyResult:
        """Price to yield calculation."""
        price = self.get(column=price_col).get_value()
        yield_val = price / 100.0 * 1.5
        self.get(column=yield_col).set_value(yield_val)
        return DependencyResult.SUCCESS

    def yield_to_yield2(self, yield_col: int, yield2_col: int) -> DependencyResult:
        """Yield to price calculation."""
        yield_val = self.get(column=yield_col).get_value()
        yield2 = yield_val * 2.001
        self.get(column=yield2_col).set_value(yield2)
        return DependencyResult.SUCCESS

    def yield2_to_yield3(self, yield2_col: int, yield3_col: int) -> DependencyResult:
        """Yield to price calculation."""
        yield2_val = self.get(column=yield2_col).get_value()
        yield3 = yield2_val * 2.001
        self.get(column=yield3_col).set_value(yield3)
        return DependencyResult.SUCCESS

    def yield3_to_yield4(self, yield3_col: int, yield4_col: int) -> DependencyResult:
        """Yield to price calculation."""
        yield3_val = self.get(column=yield3_col).get_value()
        yield4 = yield3_val * 2.001
        self.get(column=yield4_col).set_value(yield4)
        return DependencyResult.SUCCESS

    def yield4_to_price(self, yield4_col: int, price_col: int) -> DependencyResult:
        """Yield to price calculation."""
        yield4_val = self.get(column=yield4_col).get_value()
        price = (yield4_val / 8.012) / 1.5 * 100.0
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
        self.add_dependency('yield', 'yield2', self.yield_to_yield2)
        self.add_dependency('yield2', 'yield3', self.yield2_to_yield3)
        self.add_dependency('yield3', 'yield4', self.yield3_to_yield4)
        self.add_dependency('yield4', 'price', self.yield4_to_price)
        self.add_dependency('price', 'dv01', self.price_to_dv01)
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

        us_bond.get(column='expiration').set_value(datetime(2019, 3, 5, 8, 23, 5, 123456))
        self.assertEqual(us_bond.get(column='price').get_value(), 100.5)
        self.assertAlmostEqual(us_bond.get(column='yield').get_value(), 1.50749999)
        self.assertAlmostEqual(us_bond.get(column='dv01').get_value(), 1.005)
        self.assertEqual(SOMETHING_TO_CHANGE, 20)

        # The circular price <-> yield dependency is being tested
        us_bond.get(column='yield').set_value(1.5075)
        self.assertAlmostEqual(us_bond.get(column='price').get_value(), 100.50007527)
        self.assertEqual(us_bond.get(column='yield').get_value(), 1.5075)
        self.assertAlmostEqual(us_bond.get(column='dv01').get_value(), 1.00500075)
        self.assertEqual(SOMETHING_TO_CHANGE, 40)

        self.assertEqual(
            us_bond.get_string(),
            'price: 100.5000752746505, -> price_to_yield,price_to_dv01,\n'
            'yield: 1.5075, -> yield_to_yield2,\n'
            'yield2: 3.0165075, -> yield2_to_yield3,\n'
            'yield3: 6.0360315075, -> yield3_to_yield4,\n'
            'yield4: 12.078099046507498, -> yield4_to_price,\n'
            'dv01: 1.005000752746505, -> dv01_action,\n'
            'expiration: 2019-03-05 08:23:05.123456,\n')

        # Now that we set the max circle count to 10, price should not exactly stay the same
        us_bond.set_dependency_circle_max(10)
        us_bond.get(column='price').set_value(100.5)
        self.assertTrue(abs(us_bond.get(column='price').get_value() - 100.5) > 0.0)
        self.assertTrue(abs(us_bond.get(column='price').get_value() - 100.5) < 0.001)
        self.assertAlmostEqual(us_bond.get(column='yield').get_value(), 1.50751016)

        with self.assertRaises(NotImplementedError):
            us_bond.remove_column('yield')
        with self.assertRaises(NotImplementedError):
            us_bond.remove_row('yield', 0)
