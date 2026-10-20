"""
Integration tests for FastAPI server endpoint handlers.
"""
import unittest
from server import (
    get_status,
    get_samples,
    get_metrics,
    analyze_email,
    batch_analyze,
    EmailAnalysisRequest,
    BatchAnalysisRequest,
    BatchItem,
)
from samples import SAMPLE_EMAILS


class TestServerEndpoints(unittest.TestCase):
    def test_get_status(self):
        status = get_status()
        self.assertEqual(status["status"], "online")
        self.assertGreater(status["models_loaded"], 0)
        self.assertGreater(status["feature_count"], 0)

    def test_get_samples(self):
        data = get_samples()
        self.assertIn("samples", data)
        self.assertGreater(len(data["samples"]), 0)

    def test_get_metrics(self):
        metrics = get_metrics()
        self.assertIn("benchmarks", metrics)
        self.assertIn("dataset_stats", metrics)
        self.assertIn("roc_data", metrics)

    def test_analyze_email_endpoint(self):
        req = EmailAnalysisRequest(
            text=SAMPLE_EMAILS[0]["body"],
            sender=SAMPLE_EMAILS[0]["sender"],
            subject=SAMPLE_EMAILS[0]["subject"]
        )
        res = analyze_email(req)
        self.assertEqual(res["verdict"], "PHISHING")
        self.assertGreaterEqual(res["risk_score"], 60.0)

    def test_batch_analyze_endpoint(self):
        items = [
            BatchItem(
                id="phish_1",
                text=SAMPLE_EMAILS[0]["body"],
                sender=SAMPLE_EMAILS[0]["sender"],
                subject=SAMPLE_EMAILS[0]["subject"]
            ),
            BatchItem(
                id="clean_1",
                text=SAMPLE_EMAILS[4]["body"],
                sender=SAMPLE_EMAILS[4]["sender"],
                subject=SAMPLE_EMAILS[4]["subject"]
            )
        ]
        req = BatchAnalysisRequest(emails=items)
        res = batch_analyze(req)
        self.assertEqual(res["total_analyzed"], 2)
        self.assertEqual(res["phishing_detected"], 1)
        self.assertEqual(res["legitimate_detected"], 1)


if __name__ == "__main__":
    unittest.main()
