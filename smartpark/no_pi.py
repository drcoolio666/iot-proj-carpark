"""Desktop launcher for the smart carpark application.

This is the entry point used when running the project on a normal computer
that does not have a Raspberry Pi or a SenseHat. A pair of tkinter windows
are created: one acts as the public display showing free bays and the other
acts as a stand in for the physical entry and exit sensors.
"""

from interfaces import CarparkSensorListener
from interfaces import CarparkDataProvider
import threading
import time
import tkinter as tk
from typing import Iterable

from carpark import CarPark


# ------------------------------------------------------------------------------------#
# You don't need to understand how to implement this class.                           #
# ------------------------------------------------------------------------------------#


class WindowedDisplay:
    """Displays values for a given set of fields as a simple GUI window.

    Use .show() to display the window; use .update() to update the values
    displayed.
    """

    DISPLAY_INIT = '_ _ _'
    SEP = ':'  # field name separator

    def __init__(self, root, title: str, display_fields: Iterable[str]):
        """Build a Windowed (tkinter) display to replace the sense_hat display.

        Parameters
        ----------
        title : str
            The title of the window (usually the name of the carpark).
        display_fields : Iterable
            Field names for the UI. Updates to values must be presented in
            a dictionary that uses these field names as keys.
        """
        self.window = tk.Toplevel(root)
        self.window.title(f'{title}: Parking')
        self.window.geometry('800x400')
        self.window.resizable(False, False)
        self.display_fields = display_fields

        self.gui_elements = {}
        for i, field in enumerate(self.display_fields):

            # create the elements
            self.gui_elements[f'lbl_field_{i}'] = tk.Label(
                self.window, text=field + self.SEP, font=('Arial', 50))
            self.gui_elements[f'lbl_value_{i}'] = tk.Label(
                self.window, text=self.DISPLAY_INIT, font=('Arial', 50))

            # position the elements
            self.gui_elements[f'lbl_field_{i}'].grid(
                row=i, column=0, sticky=tk.E, padx=5, pady=5)
            self.gui_elements[f'lbl_value_{i}'].grid(
                row=i, column=2, sticky=tk.W, padx=10)

    def show(self):
        """Display the GUI. Non blocking when launched from no_pi main."""
        pass

    def update(self, updated_values: dict):
        """Update the values displayed in the GUI.

        Expects a dictionary with keys matching the field names passed to
        the constructor.
        """
        for field in self.gui_elements:
            if field.startswith('lbl_field'):
                field_value = field.replace('field', 'value')
                self.gui_elements[field_value].configure(
                    text=updated_values[self.gui_elements[field].cget('text').rstrip(self.SEP)])
        self.window.update()


# -----------------------------------------#
# Student implementation begins here.       #
# -----------------------------------------#

class CarParkDisplay:
    """Simple public display of the carpark status.

    Polls the data provider once per second and pushes the latest numbers
    onto the windowed display. When the carpark fills up the bays count
    falls to zero and the word FULL is shown instead.
    """

    # Field names that appear in the UI window.
    fields = ['Available bays', 'Temperature', 'At']

    def __init__(self, root):
        self.window = WindowedDisplay(root, 'Moondalup', CarParkDisplay.fields)
        updater = threading.Thread(target=self.check_updates)
        updater.daemon = True
        updater.start()
        self.window.show()
        self._provider = None

    @property
    def data_provider(self):
        return self._provider

    @data_provider.setter
    def data_provider(self, provider):
        if isinstance(provider, CarparkDataProvider):
            self._provider = provider

    def update_display(self):
        """Refresh the GUI with the latest values from the data provider."""
        bays = self._provider.available_spaces
        bays_text = 'FULL' if bays == 0 else f'{bays:03d}'
        field_values = dict(zip(CarParkDisplay.fields, [
            bays_text,
            f'{self._provider.temperature:02d}C',
            time.strftime("%H:%M:%S", self._provider.current_time)
        ]))
        self.window.update(field_values)

    def check_updates(self):
        """Background loop that refreshes the display once per second."""
        while True:
            time.sleep(1)
            if self._provider is not None:
                self.update_display()


class CarDetectorWindow:
    """A couple of simple buttons that stand in for the entry and exit sensors.

    The temperature and the license plate are pulled out of the text boxes
    on the same window before being passed to every registered listener.
    """

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
        self.listeners = list()
        self.temp_label = tk.Label(
            self.root, text="Temperature", font=('Arial', 20)
        )
        self.temp_label.grid(padx=10, pady=5, column=0, row=2)
        self.temp_var = tk.StringVar()
        self.temp_var.trace_add(
            "write",
            lambda x, y, v: self.temperature_changed(self.temp_var.get())
        )
        self.temp_box = tk.Entry(
            self.root, font=('Arial', 20), textvariable=self.temp_var
        )
        self.temp_box.grid(padx=10, pady=5, column=1, row=2)

        self.plate_label = tk.Label(
            self.root, text="License Plate", font=('Arial', 20)
        )
        self.plate_label.grid(padx=10, pady=5, column=0, row=3)
        self.plate_var = tk.StringVar()
        self.plate_box = tk.Entry(
            self.root, font=('Arial', 20), textvariable=self.plate_var
        )
        self.plate_box.grid(padx=10, pady=5, column=1, row=3)

    @property
    def current_license(self):
        return self.plate_var.get()

    def add_listener(self, listener):
        if isinstance(listener, CarparkSensorListener):
            self.listeners.append(listener)

    def incoming_car(self):
        """Tell every listener that a car was just detected entering."""
        for listener in self.listeners:
            listener.incoming_car(self.current_license)

    def outgoing_car(self):
        """Tell every listener that a car was just detected leaving."""
        for listener in self.listeners:
            listener.outgoing_car(self.current_license)

    def temperature_changed(self, temp):
        """Forward a new temperature reading on to every listener."""
        # Skip blank readings so an empty entry box does not crash the loop.
        if temp is None or str(temp).strip() == "":
            return
        try:
            value = float(temp)
        except ValueError:
            return
        for listener in self.listeners:
            listener.temperature_reading(value)


if __name__ == '__main__':
    root = tk.Tk()

    # Build the real carpark manager, backed by the project config file.
    manager = CarPark()

    display = CarParkDisplay(root)
    display.data_provider = manager

    detector = CarDetectorWindow(root)
    detector.add_listener(manager)

    root.mainloop()
