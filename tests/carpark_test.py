"""Tests for the CarPark manager.

The tests cover the main behaviours the lecturer asked for: the carpark
correctly parses its configuration file, the available bay count goes up
and down by exactly one per event, the count never drops below zero, and
unknown plates do not free up a bay.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Make the smartpark package importable when running the tests directly.
cwd = Path(os.path.dirname(__file__))
parent = str(cwd.parent)
sys.path.append(parent + "/smartpark")

from carpark import CarPark


def _build_config(total_spaces=5, location="Moondalup"):
    """Helper that writes a tiny config file used by every test below."""
    config_string = {
        "CarParks": [
            {
                "name": "test_carpark",
                "total-spaces": total_spaces,
                "total-cars": 0,
                "location": location,
                "broker": "localhost",
                "port": 1883,
                "Sensors": [
                    {"name": "sensor1", "type": "entry"},
                    {"name": "sensor2", "type": "exit"}
                ],
                "Displays": [
                    {"name": "display1"}
                ]
            }
        ]
    }
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(config_string, tmp)
    tmp.close()
    return tmp.name


class TestCarParkConfiguration(unittest.TestCase):
    """Validates that the CarPark reads its initial state from the config."""

    def setUp(self):
        self.config_path = _build_config(total_spaces=10, location="Moondalup")
        self.log_path = tempfile.NamedTemporaryFile(
            "w", suffix=".log", delete=False).name

    def tearDown(self):
        for path in (self.config_path, self.log_path):
            if os.path.exists(path):
                os.unlink(path)

    def test_carpark_loads_total_spaces_and_location_from_config(self):
        """The CarPark picks up the location and capacity from the file."""
        park = CarPark(config_file=self.config_path, log_file=self.log_path)
        self.assertEqual(park.total_spaces, 10)
        self.assertEqual(park.location, "Moondalup")
        self.assertEqual(park.available_spaces, 10)


class TestCarParkEntryExit(unittest.TestCase):
    """Confirms the bay count tracks entry and exit events correctly."""

    def setUp(self):
        self.config_path = _build_config(total_spaces=3)
        self.log_path = tempfile.NamedTemporaryFile(
            "w", suffix=".log", delete=False).name
        self.park = CarPark(config_file=self.config_path,
                            log_file=self.log_path)

    def tearDown(self):
        for path in (self.config_path, self.log_path):
            if os.path.exists(path):
                os.unlink(path)

    def test_available_spaces_drops_by_one_when_a_car_enters(self):
        """A successful entry reduces the bay count by exactly one."""
        starting = self.park.available_spaces
        self.park.incoming_car("ABC123", car_model="Toyota Corolla")
        self.assertEqual(self.park.available_spaces, starting - 1)

    def test_available_spaces_rises_by_one_when_a_known_car_exits(self):
        """A successful exit returns the bay back to the free pool."""
        self.park.incoming_car("ABC123", car_model="Toyota Corolla")
        before_exit = self.park.available_spaces
        self.park.outgoing_car("ABC123")
        self.assertEqual(self.park.available_spaces, before_exit + 1)


class TestCarParkEdgeCases(unittest.TestCase):
    """Boundary checks for the bay count: no negatives, no phantom exits."""

    def setUp(self):
        # Very small lot so the test can fill it quickly.
        self.config_path = _build_config(total_spaces=2)
        self.log_path = tempfile.NamedTemporaryFile(
            "w", suffix=".log", delete=False).name
        self.park = CarPark(config_file=self.config_path,
                            log_file=self.log_path)

    def tearDown(self):
        for path in (self.config_path, self.log_path):
            if os.path.exists(path):
                os.unlink(path)

    def test_available_spaces_does_not_go_below_zero(self):
        """When the lot is already full, extra entries are rejected."""
        # Fill the two bays.
        self.park.incoming_car("AAA111")
        self.park.incoming_car("BBB222")
        self.assertEqual(self.park.available_spaces, 0)
        # Two more cars try to enter; both should be turned away.
        self.park.incoming_car("CCC333")
        self.park.incoming_car("DDD444")
        self.assertEqual(self.park.available_spaces, 0)

    def test_unknown_plate_exit_does_not_free_a_bay(self):
        """An exit event for a plate the system has never seen is ignored."""
        self.park.incoming_car("AAA111")
        before = self.park.available_spaces
        self.park.outgoing_car("ZZZ999")  # never entered
        self.assertEqual(self.park.available_spaces, before)

    def test_temperature_reading_is_stored_for_display(self):
        """A new temperature reading replaces the previous one."""
        self.park.temperature_reading(24.6)
        self.assertEqual(self.park.temperature, 24)
        self.park.temperature_reading(31.2)
        self.assertEqual(self.park.temperature, 31)


if __name__ == "__main__":
    unittest.main()
