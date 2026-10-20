"""
Unit tests for text processing and structural email feature extraction.
"""
import unittest
from email.message import EmailMessage

from run_simple import (
    clean_text,
    get_urls,
    feat_nurls,
    feat_ndots,
    feat_nports,
    feat_checkdomains,
    feat_hashtml,
    feat_badwords,
    feat_diffhref,
    feat_ipurls,
    feat_forms,
    feat_scripts,
)


class TestFeatureExtraction(unittest.TestCase):
    def test_clean_text_normalisation(self):
        sample = "URGENT!! Please click HERE to verify your account: https://example.com/login"
        cleaned = clean_text(sample)
        # Should replace URLs with 'url'
        self.assertIn("url", cleaned)
        self.assertNotIn("https://example.com/login", cleaned)

    def test_url_extraction(self):
        sample_html = '<a href="https://bank.com/login">Login</a> and <a href="http://192.168.1.1/steal">Verify</a>'
        msg = EmailMessage()
        msg.set_content(sample_html, subtype="html")
        urls = get_urls(msg)
        self.assertEqual(len(urls), 2)
        self.assertIn("https://bank.com/login", urls)
        self.assertIn("http://192.168.1.1/steal", urls)

    def test_structural_feature_ip_and_diffhref(self):
        msg = EmailMessage()
        msg["From"] = "security@paypal.com"
        msg.set_content(
            '<html><body>'
            '<p>Your account is suspended.</p>'
            '<a href="http://192.168.1.100/login">https://www.paypal.com/signin</a>'
            '<form action="http://phish.ru/post"><input name="p"></form>'
            '<script>stealCookies();</script>'
            '</body></html>',
            subtype="html"
        )
        # 3 URLs: the href link, the visible url in anchor text, and the form action
        self.assertEqual(feat_nurls(msg), 3)
        self.assertEqual(feat_ipurls(msg), 1)
        self.assertEqual(feat_diffhref(msg), 1)
        self.assertEqual(feat_forms(msg), 1)
        self.assertEqual(feat_scripts(msg), 1)
        self.assertEqual(feat_hashtml(msg), 1)
        self.assertEqual(feat_checkdomains(msg), 0)  # Deviates from paypal.com

    def test_clean_email_structural_integrity(self):
        msg = EmailMessage()
        msg["From"] = "newsletter@company.com"
        msg["To"] = "employee@company.com"
        msg["Subject"] = "Weekly Engineering Standup Notes"
        msg.set_content(
            'Team, attached are the engineering standup notes from Monday.\n'
            'Please review the project documentation on https://company.com/notes.\n'
            'Regards,\nEngineering Lead'
        )
        self.assertEqual(feat_ipurls(msg), 0)
        self.assertEqual(feat_diffhref(msg), 0)
        self.assertEqual(feat_forms(msg), 0)
        self.assertEqual(feat_scripts(msg), 0)
        self.assertEqual(feat_checkdomains(msg), 1)  # Matches sender domain


if __name__ == "__main__":
    unittest.main()
