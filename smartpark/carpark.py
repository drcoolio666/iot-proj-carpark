"""Carpark module.

The CarPark class is the central controller for the Moondalup smart carpark
solution. It owns the configuration, the list of currently parked cars, and
the connection to the display. It also writes every entry and exit event to
a log file so that the parking officer can audit activity later.
"""

import json
import os
import time
from datetime import datetime

from interfaces import CarparkSensorListener, CarparkDataProvider
from car import Car


class CarPark(CarparkSensorListener, CarparkDataProvider):
    """Main carpark manager.

    Reads its setup values from a JSON configuration file, keeps track of
    every car currently in the lot, and exposes the current state through
    the properties required by the display.
    """

    def __init__(self, config_file=None, log_file="carpark_log.txt"):
        """Initialise the carpark from a configuration file.

        If no configuration file is supplied a sensible default is loaded
        from the samples_and_snippets folder. This keeps the tests and the
        demo script working without extra plumbing.
        """
        if config_file is None:
            # Walk up from this file to the project root, then point at the
            # sample config that ships with the repository.
            here = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(here)
            config_file = os.path.join(project_root,
                                       "samples_and_snippets",
                                       "config.json")

        self.config_file = config_file
        self.log_file = log_file

        config = self._load_config(config_file)

        # Pull the headline values out of the parsed config. The defaults
        # protect us against a config file missing the optional fields.
        self.name = config.get("name", "carpark")
        self.location = config.get("location", "Moondalup")
        self.total_spaces = int(config.get("total-spaces", 0))
        self.broker = config.get("broker", "localhost")
        self.port = int(config.get("port", 1883))

        # Cars currently in the lot, keyed by their plate so we can find them
        # quickly when they leave.
        self._parked_cars = {}

        # Latest temperature reading. Starts at a reasonable default until a
        # real reading comes through from the sensor.
        self._temperature = 22

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _load_config(config_file):
        """Read the JSON file from disk and return the first carpark entry.

        The file can either be a flat object describing one carpark or the
        full shape used in the sample with a "CarParks" list. Both formats
        are accepted so the class is friendly to extend later.
        """
        with open(config_file, "r") as input_file:
            data = json.load(input_file)

        if isinstance(data, dict) and "CarParks" in data:
            return data["CarParks"][0]
        return data

    # ------------------------------------------------------------------
    # CarparkDataProvider implementation
    # ------------------------------------------------------------------
    @property
    def available_spaces(self):
        """How many bays are free right now.

        Calculated rather than stored so it can never drift away from the
        true count of parked cars.
        """
        free = self.total_spaces - len(self._parked_cars)
        # Guard against the situation where more cars were detected than
        # physical bays exist. The display must never show a negative value.
        return max(0, free)

    @property
    def temperature(self):
        """Latest temperature reading in degrees Celsius."""
        return int(self._temperature)

    @property
    def current_time(self):
        """Local time as a struct_time, suitable for time.strftime."""
        return time.localtime()

    # ------------------------------------------------------------------
    # CarparkSensorListener implementation
    # ------------------------------------------------------------------
    def incoming_car(self, license_plate, car_model="Unknown"):
        """Process an entry event from the entry sensor.

        Rejects the car if the lot is already full. This was the bug that
        used to allow the available bays count to drop below zero when a
        burst of cars arrived at once.
        """
        plate = (license_plate or "").strip()
        if plate == "":
            # Without a plate we cannot tell cars apart, so just log it and
            # walk away. This protects the system from blank readings off
            # the simulator entry box.
            self._write_log("entry rejected, blank plate")
            return False

        if len(self._parked_cars) >= self.total_spaces:
            # Lot is full. Refuse the car and write a note in the log so
            # the parking officer can see how often this happens.
            self._write_log(f"entry rejected, lot full, plate {plate}")
            return False

        if plate in self._parked_cars:
            # Already inside. Don't double count.
            self._write_log(f"duplicate entry ignored for plate {plate}")
            return False

        new_car = Car(license_plate=plate, car_model=car_model)
        self._parked_cars[plate] = new_car
        self._write_log(f"entry, plate {plate}, model {car_model}")
        return True

    def outgoing_car(self, license_plate):
        """Process an exit event from the exit sensor.

        Unknown plates are logged as an anomaly but the bay count is not
        touched. This matches the requirement that unrecognised cars must
        not free up a space.
        """
        plate = (license_plate or "").strip()
        if plate == "":
            self._write_log("exit rejected, blank plate")
            return False

        if plate not in self._parked_cars:
            self._write_log(f"exit anomaly, unknown plate {plate}")
            return False

        leaving = self._parked_cars.pop(plate)
        leaving.mark_exit()
        duration_seconds = (leaving.exit_time - leaving.entry_time).total_seconds()
        self._write_log(
            f"exit, plate {plate}, parked for {int(duration_seconds)} seconds")
        return True

    def temperature_reading(self, reading):
        """Receive a new temperature reading from the sensor."""
        try:
            self._temperature = float(reading)
        except (TypeError, ValueError):
            # Bad readings are ignored so the display keeps the last good
            # value. The bad reading is recorded for the parking officer.
            self._write_log(f"bad temperature reading ignored, value {reading}")
            return
        self._write_log(f"temperature reading {self._temperature}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _write_log(self, message):
        """Append a timestamped line to the activity log."""
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{stamp} | {message}\n"
        try:
            with open(self.log_file, "a") as log:
                log.write(line)
        except OSError:
            # Logging is best effort. If the log file is not writable for
            # any reason the rest of the program should still keep working.
            pass

    # ------------------------------------------------------------------
    # Convenience helpers used by the tests
    # ------------------------------------------------------------------
    @property
    def parked_count(self):
        """Number of cars currently parked. Handy for the unit tests."""
        return len(self._parked_cars)

    def __repr__(self):
        return (f"CarPark(name={self.name!r}, location={self.location!r}, "
                f"total_spaces={self.total_spaces}, "
                f"available={self.available_spaces})")
