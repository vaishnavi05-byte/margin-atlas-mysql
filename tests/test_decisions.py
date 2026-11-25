import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from build_decisions import enrich, summarize, wilson, scenario


class DecisionContractTests(unittest.TestCase):
    def order(self, **changes):
        r=dict(order_id='1',customer_id='1',category_id='1',channel_id='1',
               order_date='2026-01-01',promised_date='2026-01-04',delivered_date='2026-01-05',status='Delivered',
               gross_paise='10000',discount_paise='1000',refund_paise='9000',cogs_paise='5000',
               recovered_inventory_paise='3000',fulfilment_paise='500',payment_fee_paise='200',reverse_logistics_paise='300',
               net_sales_paise='0',net_product_cost_paise='2000',contribution_before_marketing_paise='-3000',
               return_flag='1',late_flag='1',delivery_eligible='1',return_mature='1',new_customer='1')
        r.update(changes); return r

    def load(self, rows):
        return enrich(rows,{'1':{'region':'East'}},{'1':{'category':'Apparel'}},{'1':{'channel':'Organic'}})

    def test_loss_exposure_does_not_net_away_negative_orders(self):
        loss=self.order()
        profit=self.order(order_id='2',refund_paise='0',recovered_inventory_paise='0',reverse_logistics_paise='0',
                          net_sales_paise='9000',net_product_cost_paise='5000',contribution_before_marketing_paise='3300',return_flag='0')
        summary=summarize(self.load([loss,profit]),['segment_key'])[0]
        self.assertEqual(summary['negative_contribution_paise'],3000)
        self.assertEqual(summary['contribution_before_marketing_paise'],300)
        self.assertEqual(summary['orders'],2)

    def test_duplicate_and_orphan_inputs_fail(self):
        with self.assertRaises(ValueError): self.load([self.order(),self.order()])
        with self.assertRaises(ValueError): self.load([self.order(customer_id='99')])

    def test_invalid_financial_identity_fails(self):
        with self.assertRaises(ValueError): self.load([self.order(net_sales_paise='1')])

    def test_recent_delivery_cannot_be_flagged_mature(self):
        with self.assertRaises(ValueError): self.load([self.order(delivered_date='2026-09-10')])

    def test_wilson_zero_denominator_and_extremes(self):
        self.assertEqual(wilson(0,0),(None,None))
        self.assertAlmostEqual(wilson(0,100)[1],0.0369934982)
        self.assertAlmostEqual(wilson(100,100)[0],0.9630065018)

    def test_scenario_cost_is_for_all_mature_orders(self):
        row={'scenario_return_base_paise':100000,'return_mature':100}
        self.assertEqual(scenario(row,20,100)['modeled_net_change_paise'],10000)
        self.assertEqual(scenario(row,0,100)['modeled_net_change_paise'],-10000)
        self.assertEqual(scenario(row,20,100)['break_even_cost_per_mature_order_paise'],200)
        with self.assertRaises(ValueError): scenario(row,101,0)


if __name__=='__main__': unittest.main()
