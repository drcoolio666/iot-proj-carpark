"""Tests for the configuration parser.

These tests confirm the CarPark application can load its setup values from
the JSON configuration file that ships with the project. The parser is the
first thing that runs at startup, so if it breaks nothing else works.
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

import config_parser


class TestConfigParsing(unittest.TestCase):
    """Confirms the parser pulls the right values out of the config file."""

    def test_parse_config_reads_total_spaces_and_location(self):
        """The parser returns the location and total spaces from the file."""
        config_string = '''
        {
            "CarParks": [
                {
                    "name": "moondalup_city_square",
                    "total-spaces": 130,
                    "total-cars": 0,
                    "location": "Moondalup",
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
        '''
        with tempfile.NamedTemporaryFile("w", suffix=".json",
                                         delete=False) as tmp:
            tmp.write(config_string)
            tmp_path = tmp.name

        try:
            parking_lot = config_parser.parse_config(tmp_path)
        finally:
            os.unlink(tmp_path)

        self.assertEqual(parking_lot["location"], "Moondalup")
        self.assertEqual(parking_lot["total-spaces"], 130)
        self.assertEqual(parking_lot["name"], "moondalup_city_square")

    def test_parse_config_accepts_flat_object(self):
        """A flat config object (no CarParks wrapper) is also accepted."""
        flat_config = {
            "name": "flat_test_park",
            "total-spaces": 50,
            "location": "TestVille"
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json",
                                         delete=False) as tmp:
            json.dump(flat_config, tmp)
            tmp_path = tmp.name

        try:
            parsed = config_parser.parse_config(tmp_path)
        finally:
            os.unlink(tmp_path)

        self.assertEqual(parsed["total-spaces"], 50)
        self.assertEqual(parsed["location"], "TestVille")


if __name__ == "__main__":
    unittest.main()
