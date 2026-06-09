"""Car module.

Holds the Car class used to represent a single vehicle moving through the
carpark. Each car keeps its own identification details along with the times it
was first seen at the entry sensor and when it left through the exit sensor.
"""

from datetime import datetime


class Car:
    """Represents a single car using the carpark.

    Attributes:
        license_plate (str): The number plate string, used as a unique id.
        car_model (str): The make or model description of the vehicle.
        entry_time (datetime): The moment the car drove past the entry sensor.
        exit_time (datetime): The moment the car drove past the exit sensor.
                              Stays as None while the car is still parked.
    """

    def __init__(self, license_plate, car_model="Unknown",
                 entry_time=None, exit_time=None):
        """Build a new Car record.

        The entry time defaults to "now" if the caller does not set one. This
        keeps the call site clean for the common case where a car was just
        detected entering the bay area.
        """
        self.license_plate = license_plate
        self.car_model = car_model
        # If no entry time was supplied, stamp it as the current time so the
        # log always records when the car was first noticed by the system.
        self.entry_time = entry_time if entry_time is not None else datetime.now()
        self.exit_time = exit_time

    def mark_exit(self):
        """Stamp the current time as the exit time for this car."""
        self.exit_time = datetime.now()

    def __repr__(self):
        """Readable form mainly used when debugging."""
        return (f"Car(plate={self.license_plate!r}, "
                f"model={self.car_model!r}, "
                f"entry={self.entry_time}, exit={self.exit_time})")
