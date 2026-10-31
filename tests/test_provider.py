"""
Unit tests for FileProvider (Milestone M0).
Can be executed with: python -m unittest tests/test_provider.py
"""

import unittest
import asyncio
from datetime import date
from agent.providers.file_provider import FileProvider


class TestFileProvider(unittest.TestCase):
    def setUp(self):
        self.provider = FileProvider()

    def test_get_emails(self):
        emails = asyncio.run(self.provider.get_emails())
        self.assertGreaterEqual(len(emails), 1)
        first = emails[0]
        self.assertTrue(hasattr(first, "subject"))
        self.assertTrue(hasattr(first, "body"))

    def test_get_lms_items(self):
        items = asyncio.run(self.provider.get_lms_items())
        self.assertGreaterEqual(len(items), 1)
        first = items[0]
        self.assertTrue(hasattr(first, "title"))
        self.assertTrue(hasattr(first, "content"))

    def test_get_busy_events(self):
        # 1 week: Monday Nov 2, 2026 to Sunday Nov 8, 2026
        events = asyncio.run(self.provider.get_busy_events(date(2026, 11, 2), date(2026, 11, 8)))
        self.assertGreaterEqual(len(events), 1)
        first = events[0]
        self.assertTrue(hasattr(first, "event_key"))
        self.assertTrue(hasattr(first, "start"))
        self.assertTrue(hasattr(first, "end"))


if __name__ == "__main__":
    unittest.main()

