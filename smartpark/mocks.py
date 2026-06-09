"""Legacy shim kept only for backward compatibility.

The real implementation now lives in carpark.py. This file re-exports the
CarPark class under its old MockCarparkManager name so any older import
path keeps working until the references are cleaned up.
"""

from carpark import CarPark as MockCarparkManager
from car import Car

__all__ = ["MockCarparkManager", "Car"]
