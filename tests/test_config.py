"""Tests for the config parser."""

import json
import os
import sys
import unittest
from pathlib import Path

# set up the path so we can import the config parser from the smartpark directory
cwd = Path(os.path.dirname(__file__))
parent = str(cwd.parent)
sys.path.append(parent + "/smartpark")

# now we can import the config parser to test it
import config_parser


# this test checks that the config parser correctly reads the location and total spaces from a config file.
class TestConfigParser(unittest.TestCase):

    # this test checks that the config parser correctly reads the location and total spaces from a config file.
    def test_parse_config_reads_values(self):
        """The parser pulls the location and spaces from the file."""
        config = {
            "CarParks": [
                {
                    "name": "moondalup_city_square",
                    "total-spaces": 130,
                    "location": "Moondalup",
                    "broker": "localhost",
                    "port": 1883
                }
            ]
        }
        # write the config to a file so we can test the parser
        path = "test_cfg.json"
        with open(path, "w") as f:
            json.dump(config, f)

        # now we can test the parser by reading the config file and checking that it returns the expected values
        result = config_parser.parse_config(path)
        os.remove(path)

        self.assertEqual(result["location"], "Moondalup")
        self.assertEqual(result["total-spaces"], 130)


# run the tests
if __name__ == "__main__":
    unittest.main()
