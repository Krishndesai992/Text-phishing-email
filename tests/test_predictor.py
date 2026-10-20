"""
Unit tests for the EmailPredictor inference engine and ensemble consensus.
"""
import unittest
from predictor import predictor
from samples import SAMPLE_EMAILS


class TestEmailPredictor(unittest.TestCase):
    def setUp(self):
        self.predictor = predictor

    def test_predictor_loaded(self):
        self.assertIsNotNone(self.predictor.bundle)
        self.assertGreater(len(self.predictor.models), 0)
        self.assertGreater(len(self.predictor.feature_names), 0)

    def test_phishing_detection(self):
        # Sample 0 is the PayPal Urgent Account Suspension Phish
        phish_sample = SAMPLE_EMAILS[0]
        res = self.predictor.analyze_email(
            raw_input=phish_sample["body"],
            sender=phish_sample["sender"],
            subject=phish_sample["subject"]
        )
        self.assertTrue(res["is_phishing"])
        self.assertEqual(res["verdict"], "PHISHING")
        self.assertGreaterEqual(res["risk_score"], 60.0)
        self.assertIn("red_flags", res)
        self.assertGreater(len(res["red_flags"]), 0)
        self.assertIn("models_breakdown", res)
        self.assertGreater(len(res["models_breakdown"]), 0)

    def test_clean_detection(self):
        # Sample 4 is the Legitimate Enron Meeting Notice
        clean_sample = SAMPLE_EMAILS[4]
        res = self.predictor.analyze_email(
            raw_input=clean_sample["body"],
            sender=clean_sample["sender"],
            subject=clean_sample["subject"]
        )
        self.assertFalse(res["is_phishing"])
        self.assertEqual(res["verdict"], "LEGITIMATE")
        self.assertLessEqual(res["risk_score"], 50.0)

    def test_raw_rfc822_parsing(self):
        raw_rfc822 = (
            "From: alerts@bank-security-support.ru\r\n"
            "To: victim@target.com\r\n"
            "Subject: Immediate action required: verify debit card\r\n"
            "Content-Type: text/html\r\n\r\n"
            "<html><body>"
            "<p>Click <a href='http://192.168.1.50/steal'>here</a> to verify.</p>"
            "</body></html>"
        )
        res = self.predictor.analyze_email(raw_input=raw_rfc822)
        self.assertTrue(res["is_phishing"])
        self.assertIn("risk_score", res)


if __name__ == "__main__":
    unittest.main()
