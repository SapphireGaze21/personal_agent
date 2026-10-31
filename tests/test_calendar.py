"""
Unit tests for Calendar Utilities (Milestone M1).
Tests free_slots calculation and exceptions_store.
Can be executed with: python -m unittest tests/test_calendar.py
"""

import unittest
import tempfile
import os
from pathlib import Path
from datetime import date, datetime, time, timezone

from agent.models import CalendarEvent, Slot
from agent.calendar.exceptions_store import (
    load_exceptions,
    save_exceptions,
    add_exception,
    is_cancelled,
    get_exception,
)
from agent.calendar.free_slots import compute_free_slots, parse_time_str


class TestExceptionsStore(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = Path(self.temp_dir.name) / "exceptions.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_empty_store(self):
        excs = load_exceptions(self.test_file)
        self.assertEqual(excs, [])

    def test_add_and_load_exception(self):
        add_exception("cal1|os_class|2026-11-02", "2026-11-02", status="cancelled", note="prof sick", file_path=self.test_file)
        excs = load_exceptions(self.test_file)
        self.assertEqual(len(excs), 1)
        self.assertEqual(excs[0]["event_key"], "cal1|os_class|2026-11-02")
        self.assertEqual(excs[0]["status"], "cancelled")

    def test_is_cancelled(self):
        add_exception("cal1|os_class|2026-11-02", "2026-11-02", status="cancelled", file_path=self.test_file)
        self.assertTrue(is_cancelled("cal1|os_class|2026-11-02", "2026-11-02", file_path=self.test_file))
        self.assertFalse(is_cancelled("cal1|os_class|2026-11-03", "2026-11-03", file_path=self.test_file))
        self.assertFalse(is_cancelled("cal1|dbms_class|2026-11-02", "2026-11-02", file_path=self.test_file))

    def test_update_existing_exception(self):
        add_exception("cal1|os_class|2026-11-02", "2026-11-02", status="cancelled", note="note 1", file_path=self.test_file)
        add_exception("cal1|os_class|2026-11-02", "2026-11-02", status="moved", note="moved to afternoon", file_path=self.test_file)
        excs = load_exceptions(self.test_file)
        self.assertEqual(len(excs), 1)
        self.assertEqual(excs[0]["status"], "moved")
        self.assertEqual(excs[0]["note"], "moved to afternoon")


class TestFreeSlots(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_exceptions_file = Path(self.temp_dir.name) / "exceptions.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_time_str(self):
        t = parse_time_str("09:30")
        self.assertEqual(t, time(9, 30))
        self.assertEqual(parse_time_str(time(14, 0)), time(14, 0))

    def test_free_slots_no_events(self):
        # 1 day from 08:00 to 10:00 with 30 min slots -> 4 slots
        target_date = date(2026, 11, 2)
        slots = compute_free_slots(
            busy_events=[],
            start_date=target_date,
            end_date=target_date,
            exceptions_path=self.test_exceptions_file,
            day_start_str="08:00",
            day_end_str="10:00",
            slot_minutes=30,
        )
        self.assertEqual(len(slots), 4)
        self.assertEqual(slots[0].start, time(8, 0))
        self.assertEqual(slots[0].end, time(8, 30))
        self.assertEqual(slots[3].start, time(9, 30))
        self.assertEqual(slots[3].end, time(10, 0))

    def test_free_slots_with_busy_event(self):
        target_date = date(2026, 11, 2)
        # Busy event from 09:00 to 11:00
        busy_event = CalendarEvent(
            event_key="cal1|os_lecture|2026-11-02",
            title="Operating Systems",
            start=datetime(2026, 11, 2, 9, 0),
            end=datetime(2026, 11, 2, 11, 0),
        )

        slots = compute_free_slots(
            busy_events=[busy_event],
            start_date=target_date,
            end_date=target_date,
            exceptions_path=self.test_exceptions_file,
            day_start_str="08:00",
            day_end_str="12:00",
            slot_minutes=30,
        )

        # Total window 08:00 to 12:00 = 8 slots (4 hours)
        # Busy 09:00 to 11:00 = 4 slots (2 hours)
        # Free: 08:00-09:00 (2 slots) and 11:00-12:00 (2 slots) = 4 slots
        self.assertEqual(len(slots), 4)
        # Check that no slot falls between 09:00 and 11:00
        for s in slots:
            self.assertTrue(s.end <= time(9, 0) or s.start >= time(11, 0))

    def test_free_slots_cancelled_event_frees_up_time(self):
        target_date = date(2026, 11, 2)
        event_key = "cal1|os_lecture|2026-11-02"
        busy_event = CalendarEvent(
            event_key=event_key,
            title="Operating Systems",
            start=datetime(2026, 11, 2, 9, 0),
            end=datetime(2026, 11, 2, 11, 0),
        )

        # Before cancelling: 4 slots
        slots_before = compute_free_slots(
            busy_events=[busy_event],
            start_date=target_date,
            end_date=target_date,
            exceptions_path=self.test_exceptions_file,
            day_start_str="08:00",
            day_end_str="12:00",
            slot_minutes=30,
        )
        self.assertEqual(len(slots_before), 4)

        # Cancel the event in exceptions_store
        add_exception(event_key, "2026-11-02", status="cancelled", file_path=self.test_exceptions_file)

        # After cancelling: the busy event is ignored, full 08:00-12:00 window is free (8 slots)
        slots_after = compute_free_slots(
            busy_events=[busy_event],
            start_date=target_date,
            end_date=target_date,
            exceptions_path=self.test_exceptions_file,
            day_start_str="08:00",
            day_end_str="12:00",
            slot_minutes=30,
        )
        self.assertEqual(len(slots_after), 8)


if __name__ == "__main__":
    unittest.main()

