"""CarPark class for the smart carpark project."""

import json
import os
import time
from datetime import datetime

from interfaces import CarparkSensorListener, CarparkDataProvider
from car import Car


## Main CarPark class
# This is the main class that you will need to implement. 
# It should inherit from both CarparkSensorListener and CarparkDataProvider, and implement all of the
# abstract methods in those classes. You can also add any helper methods you like,
# and any additional properties or attributes you need to manage the carpark. 
# The only requirements are that you implement the methods in the abstract classes, 
# and that you write to the log file whenever a car enters or leaves, or when a new temperature reading is received.
class CarPark(CarparkSensorListener, CarparkDataProvider):
    """Main carpark manager. Reads config, tracks cars, writes a log."""

    # constructor
    def __init__(self, config_file=None, log_file="carpark_log.txt"):
        # default config path if none was passed in
        if config_file is None:
            here = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(here)
            config_file = os.path.join(project_root,
                                       "samples_and_snippets",
                                       "config.json")

        self.config_file = config_file
        self.log_file = log_file

        # read the config and pull out the values we need
        with open(config_file) as f:
            data = json.load(f)
        if "CarParks" in data:
            config = data["CarParks"][0]
        else:
            config = data

        self.name = config.get("name", "carpark")
        self.location = config.get("location", "Moondalup")
        self.total_spaces = int(config.get("total-spaces", 0))

        # list of cars currently in the lot
        self.cars = []

        # last temperature reading
        self.temp = 22

    # properties for the display
    @property
    def available_spaces(self):
        free = self.total_spaces - len(self.cars)
        if free < 0:
            return 0
        return free

    # for the display
    @property
    def temperature(self):
        return int(self.temp)

    # for the display
    @property
    def current_time(self):
        return time.localtime()

    # sensor listener methods
    def incoming_car(self, plate, model="Unknown"):
        # ignore blank plates
        if plate is None or str(plate).strip() == "":
            return
        plate = str(plate).strip()

        # do not let the carpark go over capacity
        if len(self.cars) >= self.total_spaces:
            self.write_log("entry rejected, carpark is full, plate " + plate)
            return

        # check if the car is already inside
        for c in self.cars:
            if c.plate == plate:
                self.write_log("duplicate entry ignored for " + plate)
                return

        # add the car to the list of cars in the lot, and write to the log
        new_car = Car(plate, model)
        self.cars.append(new_car)
        self.write_log("car entered, plate " + plate + ", model " + model)

    # for the display
    def outgoing_car(self, plate):
        if plate is None or str(plate).strip() == "":
            return
        plate = str(plate).strip()

        # find the car and remove it
        found = None
        for c in self.cars:
            if c.plate == plate:
                found = c
                break

        if found is None:
            # unknown plate, do not free a space
            self.write_log("exit ignored, unknown plate " + plate)
            return

        found.set_exit()
        self.cars.remove(found)
        self.write_log("car left, plate " + plate)

    # this method will be called whenever a new temperature reading is received. 
    # You should update the temp property, and write to the log.
    def temperature_reading(self, reading):
        try:
            self.temp = float(reading)
        except (TypeError, ValueError):
            return
        self.write_log("temperature is " + str(self.temp))

    # helper to write to the log file
    def write_log(self, message):
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = stamp + " " + message + "\n"
        with open(self.log_file, "a") as log:
            log.write(line)
