"""Tests for the CarPark class."""

import json
import os
import sys
import unittest
from pathlib import Path

# set up the path so we can import the CarPark class from the smartpark directory
cwd = Path(os.path.dirname(__file__))
parent = str(cwd.parent)
sys.path.append(parent + "/smartpark")

# now we can import the CarPark class
from carpark import CarPark

# helper function to create a config file for the tests
# this is used in the setUp method of the test class to create a config file with a specified number of spaces
def make_test_config(spaces=5):
    """Write a small config file used by the tests."""
    config = {
        "CarParks": [
            {
                "name": "test_park",
                "total-spaces": spaces,
                "location": "Moondalup",
                "broker": "localhost",
                "port": 1883
            }
        ]
    }
    path = "test_config.json"
    with open(path, "w") as f:
        json.dump(config, f)
    return path

# now we can write the tests for the CarPark class
# these tests will check that the CarPark class correctly reads the config file, 
# updates the available spaces when cars enter and leave, and handles edge cases 
# like trying to park when the lot is full or trying to leave with an unknown car.
class TestCarPark(unittest.TestCase):

    # the setUp method is called before each test method to set up the test environment
    def setUp(self):        
        self.config_path = make_test_config(spaces=3)
        self.log_path = "test_log.txt"
        self.park = CarPark(self.config_path, self.log_path)

    # the tearDown method is called after each test method to clean up the test environment
    def tearDown(self):
        # clean up the test files
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    # now we can write the individual test methods to check the functionality of the CarPark class
    def test_carpark_reads_config(self):
        """The carpark loads the total spaces from the config file."""
        self.assertEqual(self.park.total_spaces, 3)
        self.assertEqual(self.park.location, "Moondalup")

    # the following tests check the behavior of the CarPark class when cars enter and leave the lot,
    # and also check edge cases like trying to park when the lot is full or trying to leave with an unknown car.
    def test_car_entering_reduces_available_spaces_by_one(self):
        """When a car enters the available spaces should drop by one."""
        before = self.park.available_spaces
        self.park.incoming_car("AAA111", "Toyota")
        self.assertEqual(self.park.available_spaces, before - 1)

    # the following test checks that when a known car leaves the lot, the available spaces increases by one.
    def test_car_leaving_adds_back_a_space(self):
        """When a known car leaves the space comes back."""
        self.park.incoming_car("AAA111", "Toyota")
        before = self.park.available_spaces
        self.park.outgoing_car("AAA111")
        self.assertEqual(self.park.available_spaces, before + 1)

    # the following test checks that if the lot is full, 
    # trying to park another car does not reduce the available spaces below zero.
    def test_available_spaces_never_goes_below_zero(self):
        """If the lot is full, more entries should be rejected."""
        self.park.incoming_car("AAA111")
        self.park.incoming_car("BBB222")
        self.park.incoming_car("CCC333")
        # the lot is full now
        self.park.incoming_car("DDD444")
        self.park.incoming_car("EEE555")
        self.assertEqual(self.park.available_spaces, 0)

    # the following test checks that if a car that the system never saw tries to leave,
    # it should be ignored and the available spaces should not change.
    def test_unknown_car_leaving_does_not_free_a_space(self):
        """If a car the system never saw tries to leave it should be ignored."""
        self.park.incoming_car("AAA111")
        before = self.park.available_spaces
        self.park.outgoing_car("ZZZ999")
        self.assertEqual(self.park.available_spaces, before)

    # the following test checks that the temperature reading is correctly stored.
    def test_temperature_is_updated(self):
        """The temperature reading should be stored."""
        self.park.temperature_reading(25)
        self.assertEqual(self.park.temperature, 25)

# the following test checks that the log file is created and contains the expected entries when cars enter and leave the lot.
if __name__ == "__main__":
    unittest.main()
