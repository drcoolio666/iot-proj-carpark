"""Desktop launcher for the smart carpark project.

Used when running on a normal computer without a Raspberry Pi or SenseHat.
Two tkinter windows are opened: one is the public display showing the bays,
temperature and time, the other one is the detector window that stands in
for the entry and exit sensors.
"""

from interfaces import CarparkSensorListener
from interfaces import CarparkDataProvider
import threading
import time
import tkinter as tk
from typing import Iterable

from carpark import CarPark


# The WindowedDisplay class is a simple tkinter window that is used as the public display. 
# It has a title and a list of fields to display. The update method takes a dictionary of updated values and updates the display accordingly.
class WindowedDisplay:
    """A simple tkinter window used as the public display."""

    DISPLAY_INIT = '_ _ _'
    SEP = ':'

    # init method to initialize the window with a title and a list of fields to display.
    def __init__(self, root, title, display_fields):
        self.window = tk.Toplevel(root)
        self.window.title(title + ': Parking')
        self.window.geometry('800x400')
        self.window.resizable(False, False)
        self.display_fields = display_fields

        self.gui_elements = {}
        # create the labels for the fields and values and store them in a dictionary for easy access 
        # when updating the display
        for i, field in enumerate(self.display_fields):
            self.gui_elements['lbl_field_' + str(i)] = tk.Label(
                self.window, text=field + self.SEP, font=('Arial', 50))
            self.gui_elements['lbl_value_' + str(i)] = tk.Label(
                self.window, text=self.DISPLAY_INIT, font=('Arial', 50))

            self.gui_elements['lbl_field_' + str(i)].grid(
                row=i, column=0, sticky=tk.E, padx=5, pady=5)
            self.gui_elements['lbl_value_' + str(i)].grid(
                row=i, column=2, sticky=tk.W, padx=10)

    # method to show the window
    def show(self):
        pass

    # method to update the display with the updated values. 
    # The updated values are passed as a dictionary where the keys are the field names 
    # and the values are the updated values. 
    # The method updates the corresponding labels in the display with the new values.
    def update(self, updated_values):
        for field in self.gui_elements:
            if field.startswith('lbl_field'):
                field_value = field.replace('field', 'value')
                self.gui_elements[field_value].configure(
                    text=updated_values[self.gui_elements[field].cget('text').rstrip(self.SEP)])
        self.window.update()


# The CarParkDisplay class is the main display for the carpark. 
# It shows the available bays, the temperature and the time. 
# It uses the WindowedDisplay class to create the display and updates it with the data from the CarparkDataProvider. 
class CarParkDisplay:
    """Shows the available bays, the temperature and the time."""

    fields = ['Available bays', 'Temperature', 'At']

    # init method to initialize the display with a root window and start a thread to check for updates 
    # from the data provider.
    def __init__(self, root):
        self.window = WindowedDisplay(root, 'Moondalup', CarParkDisplay.fields)
        updater = threading.Thread(target=self.check_updates)
        updater.daemon = True
        updater.start()
        self.window.show()
        self._provider = None

    # property to get the data provider and setter to set the data provider.
    @property
    def data_provider(self):
        return self._provider

    # setter to set the data provider. The data provider must be an instance of CarparkDataProvider.
    @data_provider.setter
    def data_provider(self, provider):
        if isinstance(provider, CarparkDataProvider):
            self._provider = provider

    # method to update the display with the data from the data provider. 
    # It gets the available bays, temperature and time from the data provider and updates the display accordingly.
    def update_display(self):
        bays = self._provider.available_spaces
        if bays == 0:
            bays_text = 'FULL'
        else:
            bays_text = str(bays)
        values = dict(zip(CarParkDisplay.fields, [
            bays_text,
            str(self._provider.temperature) + 'C',
            time.strftime("%H:%M:%S", self._provider.current_time)
        ]))
        self.window.update(values)

    # method to check for updates from the data provider. It runs in a separate thread and checks for updates every second.
    def check_updates(self):
        while True:
            time.sleep(1)
            if self._provider is not None:
                self.update_display()


# The CarDetectorWindow class is a simple tkinter window that stands in for the entry and exit sensors. 
# It has two buttons, one for incoming cars and one for outgoing cars. 
# It also has a text box for the temperature and a text box for the license plate.
class CarDetectorWindow:
    """Two buttons that pretend to be the entry and exit sensors."""

    def __init__(self, root):
        self.root = root
        self.root.title("Car Detector ULTRA")

        self.btn_incoming_car = tk.Button(
            self.root, text='Incoming Car', font=('Arial', 50),
            cursor='right_side', command=self.incoming_car)
        self.btn_incoming_car.grid(padx=10, pady=5, row=0, columnspan=2)
        self.btn_outgoing_car = tk.Button(
            self.root, text='Outgoing Car', font=('Arial', 50),
            cursor='bottom_left_corner', command=self.outgoing_car)
        self.btn_outgoing_car.grid(padx=10, pady=5, row=1, columnspan=2)

        self.listeners = []

        self.temp_label = tk.Label(
            self.root, text="Temperature", font=('Arial', 20))
        self.temp_label.grid(padx=10, pady=5, column=0, row=2)
        self.temp_var = tk.StringVar()
        self.temp_var.trace_add(
            "write",
            lambda x, y, v: self.temperature_changed(self.temp_var.get()))
        self.temp_box = tk.Entry(
            self.root, font=('Arial', 20), textvariable=self.temp_var)
        self.temp_box.grid(padx=10, pady=5, column=1, row=2)

        self.plate_label = tk.Label(
            self.root, text="License Plate", font=('Arial', 20))
        self.plate_label.grid(padx=10, pady=5, column=0, row=3)
        self.plate_var = tk.StringVar()
        self.plate_box = tk.Entry(
            self.root, font=('Arial', 20), textvariable=self.plate_var)
        self.plate_box.grid(padx=10, pady=5, column=1, row=3)

    # property to get the current license plate from the text box.
    @property
    def current_license(self):
        return self.plate_var.get()

    # method to add a listener to the list of listeners. The listener must be an instance of CarparkSensorListener.
    def add_listener(self, listener):
        if isinstance(listener, CarparkSensorListener):
            self.listeners.append(listener)

    # method called when an incoming car is detected.
    def incoming_car(self):
        for listener in self.listeners:
            listener.incoming_car(self.current_license)

    # method called when an outgoing car is detected.
    def outgoing_car(self):
        for listener in self.listeners:
            listener.outgoing_car(self.current_license)

    # method called when the temperature is changed.
    def temperature_changed(self, temp):
        if temp is None or str(temp).strip() == "":
            return
        try:
            value = float(temp)
        except ValueError:
            return
        for listener in self.listeners:
            listener.temperature_reading(value)


# The main function creates the root window, the car park manager, the display and the detector. 
# It sets the data provider for the display to the car park manager and adds the car park manager 
# as a listener to the detector. Finally, it starts the main loop of the tkinter application.
if __name__ == '__main__':
    root = tk.Tk()
    manager = CarPark()
    display = CarParkDisplay(root)
    display.data_provider = manager
    detector = CarDetectorWindow(root)
    detector.add_listener(manager)
    root.mainloop()
