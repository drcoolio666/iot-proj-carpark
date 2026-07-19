"""Car class for the carpark project."""

# import datetime to track the entry and exit times of the car
from datetime import datetime


# the car class represents a car that uses the carpark. It has a plate number, model, entry time, and exit time.
class Car:
    """A car that uses the carpark."""

    # init method to initialize the car with a plate number and model. 
    # The entry time is set to the current time when the car is created, 
    # and the exit time is set to None until the car leaves.
    def __init__(self, plate, model="Unknown"):
        # plate is used as the id for the car
        self.plate = plate
        self.model = model
        self.entry_time = datetime.now()
        self.exit_time = None

    # method to set the exit time when the car leaves
    def set_exit(self):
        # called when the car leaves
        self.exit_time = datetime.now()
