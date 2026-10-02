import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from radar_metrics import summarize, trailing_return

class RadarTests(unittest.TestCase):
    def test_return_and_distribution_are_not_double_counted(self):
        rows=[{'date':'2025-01-01','close':100},{'date':'2025-07-01','close':105},{'date':'2026-01-01','close':110}]
        result=summarize(rows,[{'date':'2025-09-01','amount':2}],100,{})
        self.assertAlmostEqual(result['r1'],10)
        self.assertEqual(result['yieldTTM'],2)
        self.assertIsNone(result['r3'])
        self.assertIsNone(result['analyst'])
    def test_missing_income_is_not_zero_and_undated_consensus_marked(self):
        rows=[{'date':'2025-01-01','close':100},{'date':'2025-07-01','close':105},{'date':'2026-01-01','close':110}]
        result=summarize(rows,[],100,{'targetMeanPrice':120,'numberOfAnalystOpinions':4})
        self.assertIsNone(result['incomeTTM']);self.assertIsNone(result['yieldTTM'])
        self.assertIsNone(result['analyst']['referenceDate'])
        self.assertAlmostEqual(result['analyst']['upside'],20)
    def test_insufficient_window_and_invalid_target_not_extrapolated(self):
        rows=[{'date':'2025-02-01','close':100},{'date':'2025-07-01','close':105},{'date':'2026-01-01','close':110}]
        self.assertIsNone(trailing_return(rows,1))
        self.assertIsNone(summarize(rows,[],100,{'targetMeanPrice':float('nan'),'numberOfAnalystOpinions':4})['analyst'])

if __name__=='__main__':unittest.main()
