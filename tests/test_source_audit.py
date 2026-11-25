"""Real snapshot mutation tests for grain and reconciliation failures."""
import csv
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from audit_source import audit

class SourceAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp_root=(ROOT/'tmp/tests').resolve()
        self.temp_root.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=self.temp_root)
        self.source=Path(self.temp.name)/'source'
        shutil.copytree(ROOT/'data/source',self.source)
    def tearDown(self):
        assert self.temp_root in Path(self.temp.name).resolve().parents
        self.temp.cleanup()
    def mutate(self,name,change):
        p=self.source/name
        with p.open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f);rows=list(r);fields=r.fieldnames
        change(rows)
        with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    def test_item_money_mismatch_is_rejected(self):
        self.mutate('fact_order_items.csv',lambda rows:rows[0].update(gross_paise=str(int(rows[0]['gross_paise'])+1)))
        with self.assertRaisesRegex(ValueError,'reconciliation'):audit(self.source)
    def test_missing_spend_day_is_rejected(self):
        self.mutate('fact_marketing.csv',lambda rows:rows.pop())
        with self.assertRaisesRegex(ValueError,'coverage'):audit(self.source)
    def test_duplicate_marketing_grain_is_rejected(self):
        self.mutate('fact_marketing.csv',lambda rows:rows.append(rows[0].copy()))
        with self.assertRaisesRegex(ValueError,'Duplicate source grain'):audit(self.source)

if __name__=='__main__':unittest.main()
