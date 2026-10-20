"""
Curated sample emails for testing the Phishing Email ML Classifier.
"""

SAMPLE_EMAILS = [
    {
        "id": "phish_bank",
        "category": "Phishing",
        "label": "🚨 PayPal / Bank Security Alert (Urgent Suspension)",
        "sender": "service-security@paypa1-update-alerts.com",
        "recipient": "victim@workplace.com",
        "subject": "CRITICAL: Your PayPal Account Has Been Suspended [Action Required]",
        "body": """Dear Valued Customer,

We have detected suspicious unauthorized sign-in attempts on your account from an unrecognized IP address (185.220.101.4).

To protect your funds and prevent permanent account restriction, you must verify your identity and confirm your account information within 24 hours.

Failure to verify will result in complete suspension of your online banking privileges and forfeiture of recurring payments.

Please click the secure link below to verify your credentials:
http://192.168.1.105:8080/paypal/login-verification?token=9284719284

Thank you for your prompt cooperation,
PayPal Security & Fraud Prevention Team
Copyright 2026 PayPal Inc. All rights reserved."""
    },
    {
        "id": "phish_credential",
        "category": "Phishing",
        "label": "🚨 Office 365 Password Expiration Spoof",
        "sender": "admin@it-portal-microsoft365-verify.com",
        "recipient": "employee@corporate.net",
        "subject": "Notice: Your Microsoft 365 Password Expires Today",
        "body": """IT Helpdesk Notification:

Your corporate Microsoft 365 domain password is scheduled to expire in 3 hours. 

To keep your current password and avoid losing access to your email inbox, Teams, and SharePoint files, confirm your credentials through our single sign-on portal:

Verify Current Password: <a href="http://portal.it-login-domain.com.ru/auth/sso">https://login.microsoftonline.com/keep-password</a>

If you do not verify now, your workstation will be locked out at midnight.

Corporate IT Support Services
Helpdesk Ticket Ref: #MS-883921"""
    },
    {
        "id": "phish_ceo",
        "category": "Phishing",
        "label": "🚨 CEO Wire Transfer / Gift Card Scam",
        "sender": "ceo.office.urgent@gmail.com",
        "recipient": "finance@corporate.com",
        "subject": "URGENT & CONFIDENTIAL: Wire Payment for Acquisition",
        "body": """Are you at your desk right now?

I am currently in an executive board meeting and cannot take calls. We are closing an urgent vendor retainer contract and need a wire transfer of $48,500 processed before 3:00 PM today.

Click here to view the approved invoice: http://194.87.139.24/invoices/wire_transfer_memo.pdf

Please reply as soon as you initiate the transfer. Treat this as strictly confidential.

Best regards,
Chief Executive Officer"""
    },
    {
        "id": "phish_lottery",
        "category": "Phishing",
        "label": "🚨 International Prize / Inheritance Transfer",
        "sender": "barrister.richard@claims-escrow.net",
        "recipient": "lucky.user@outlook.com",
        "subject": "URGENT CLAIM: Consignment Beneficiary Notice - USD $8.5M",
        "body": """Attn: Respected Beneficiary,

I am Barrister Richard Cole, senior legal advocate. My late foreign client shared your surname and passed away intestate leaving an unclaimed deposit of US$8,500,000.00 at an international offshore banking facility.

To link and verify yourself as the legitimate heir before the government confiscates these funds, click and confirm your private details:
http://82.165.197.1/escrow/verify_beneficiary.php?ref=48201

Send your full passport copy, full name, bank routing coordinates, and phone number.

Respectfully,
Barrister Richard Cole & Associates"""
    },
    {
        "id": "legit_meeting",
        "category": "Legitimate",
        "label": "✅ Enron Q3 Energy Trading & Pipeline Meeting",
        "sender": "phillip.allen@enron.com",
        "recipient": "mike.grigsby@enron.com",
        "subject": "Re: West Power Trading Strategy and Pipeline Capacity",
        "body": """Mike,

Regarding the West power desk models for next month, we need to adjust the basis differentials on the El Paso pipeline capacity allocations. 

Let's convene in the 32nd floor conference room tomorrow at 10:30 AM with Keith and John to review the revised spreadsheet calculations. Please bring the updated transport volume schedules.

Thanks,
Phillip"""
    },
    {
        "id": "legit_github",
        "category": "Legitimate",
        "label": "✅ GitHub Pull Request Review Notification",
        "sender": "notifications@github.com",
        "recipient": "developer@techfirm.io",
        "subject": "[GitHub] Pull Request #142: Fix async connection pool timeout",
        "body": """Hello developer,

@alex-chen requested your review on Pull Request #142: "Optimize DB connection pooling and handle reconnect backoff in cluster mode".

View Pull Request: https://github.com/organization/core-backend/pull/142

Changes: +184 lines, -42 lines in 6 files.

You can view, comment on, or approve this pull request directly on GitHub.
GitHub Inc., 88 Colin P Kelly Jr St, San Francisco, CA 94107"""
    },
    {
        "id": "legit_newsletter",
        "category": "Legitimate",
        "label": "✅ Python Weekly Engineering Digest",
        "sender": "editor@pythonweekly.com",
        "recipient": "subscriber@domain.com",
        "subject": "Python Weekly - Issue 624: Python 3.13 JIT, Polars vs Pandas",
        "body": """Welcome to the 624th issue of Python Weekly.

Here are the top engineering articles, releases, and libraries this week:
- How the new Copy-on-Write mode speeds up data pipelines
- Building distributed async workers with modern Python
- Top open source ML toolkits for email classification

Read the full issue archive at https://www.pythonweekly.com/archive/624

To manage your email preferences or unsubscribe, please visit https://www.pythonweekly.com/manage-subscription.

Happy coding!"""
    },
    {
        "id": "legit_hr",
        "category": "Legitimate",
        "label": "✅ Corporate HR Open Enrollment Reminder",
        "sender": "hr-benefits@internal-corp.com",
        "recipient": "all-employees@internal-corp.com",
        "subject": "Annual Benefits Open Enrollment Period (Nov 1 - Nov 15)",
        "body": """Dear Colleagues,

This is a reminder that our annual Health & Wellness Benefits Open Enrollment window opens this Monday and concludes on November 15.

If you wish to modify your health insurance plan, dental coverage, or contribute to flexible spending accounts (FSA/HSA), please log in to the internal HR employee portal on the company intranet:
https://intranet.internal-corp.com/hr/benefits-2026

If you are satisfied with your existing coverage selections, no action is required.

Best regards,
Global People & Culture Team"""
    }
]
