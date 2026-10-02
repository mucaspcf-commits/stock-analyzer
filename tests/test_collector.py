import importlib.util
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('collector',Path(__file__).resolve().parents[1]/'scripts/collect.py')
collector=importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)
class CollectorTests(unittest.TestCase):
    def test_preserve_does_not_change_reference_date(self):
        meta={'id':'selic','provider':'BCB'}
        previous=[{**meta,'date':'2025-01-01','fetchedAt':'2025-01-02','value':10,'history':[{'date':'2025-01-01','value':10}]}]
        actual=collector.preserve(meta,previous)
        self.assertEqual(actual['date'],'2025-01-01')
        self.assertEqual(actual['fetchedAt'],'2025-01-02')
        self.assertEqual(actual['status'],'cached')
    def test_missing_data_is_null(self):
        actual=collector.preserve({'id':'missing','provider':'BCB'},[])
        self.assertIsNone(actual['value'])
        self.assertEqual(actual['history'],[])
if __name__=='__main__':unittest.main()
