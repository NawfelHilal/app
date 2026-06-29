from decimal import Decimal

from django.test import SimpleTestCase

from apps.rides.services import FareCalculator


class FareCalculatorTests(SimpleTestCase):
    def test_commission_is_fixed_at_fifteen_percent(self):
        quote = FareCalculator().quote(Decimal("10.00"), 20)

        self.assertEqual(quote.fare_cents, 2500)
        self.assertEqual(quote.commission_cents, 375)
        self.assertEqual(quote.driver_earnings_cents, 2125)

