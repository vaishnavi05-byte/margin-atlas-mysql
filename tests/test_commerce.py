import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from commerce_metrics import discount_band, enrich_items

class CommerceContracts(unittest.TestCase):
    def test_discount_boundaries_use_exact_ratios(self):
        self.assertEqual(discount_band(10000,0),('0%',0))
        self.assertEqual(discount_band(10000,1000),('1-10%',1))
        self.assertEqual(discount_band(10000,1001),('11-20%',2))
        self.assertEqual(discount_band(10000,2000),('11-20%',2))
        self.assertEqual(discount_band(10000,2001),('21-30%',3))
        self.assertEqual(discount_band(10000,3001),('Above 30%',4))
    def test_unrecognized_sale_is_not_a_zero_discount_sale(self):
        self.assertEqual(discount_band(0,0),('No recognized sales',5))
        with self.assertRaises(ValueError):discount_band(0,1)
        with self.assertRaises(ValueError):discount_band(100,101)
    def item(self,**changes):
        row=dict(line_id='L1',order_id='O1',product_id='P1',quantity='2',gross_paise='10000',discount_paise='1000',cogs_paise='5000');row.update(changes);return row
    def test_item_margin_does_not_allocate_order_costs(self):
        orders=[dict(order_id='O1',delivery_eligible=1,refund_paise=9000,fulfilment_paise=500)]
        row=enrich_items([self.item()],orders,[{'product_id':'P1'}])[0]
        self.assertEqual(row['sales_before_refund_paise'],9000)
        self.assertEqual(row['merchandise_margin_paise'],4000)
        self.assertEqual(row['recognized_units'],2)
        self.assertNotIn('contribution_paise',row)
    def test_undelivered_line_quantity_is_not_recognized_demand(self):
        row=enrich_items([self.item(gross_paise='0',discount_paise='0',cogs_paise='0')],[dict(order_id='O1',delivery_eligible=0)],[{'product_id':'P1'}])[0]
        self.assertEqual(row['recognized_units'],0)
        self.assertEqual(row['sales_before_refund_paise'],0)
    def test_item_duplicate_and_orphan_fail(self):
        orders=[dict(order_id='O1',delivery_eligible=1)];products=[{'product_id':'P1'}]
        with self.assertRaises(ValueError):enrich_items([self.item(),self.item()],orders,products)
        with self.assertRaises(ValueError):enrich_items([self.item(order_id='missing')],orders,products)

if __name__=='__main__':unittest.main()
