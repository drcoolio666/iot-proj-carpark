# Smart Carpark Project: City of Moondalup

This repository holds my submission for AT3 Project Option 1. The project is a
small object oriented Python application that simulates a smart carpark in the
City of Moondalup. It reads configuration from a JSON file, processes car entry
and exit events from a simulated sensor, writes activity to a log file, and
shows the number of free bays and the current temperature on a windowed display.

## Scenario

I worked the role of a junior software innovation engineer for the City of
Moondalup, Department of Transport. The city wants to upgrade a number of
public carparks by providing live information about the number of available
parking bays.

## Project layout

```text
.
|-- docs/
|   |-- requirements.md
|   |-- high_level_design.md
|   `-- flowdiagram.md
|-- samples_and_snippets/
|   `-- config.json
|-- smartpark/
|   |-- car.py
|   |-- carpark.py
|   |-- config.json
|   |-- config_parser.py
|   |-- interfaces.py
|   `-- no_pi.py
|-- tests/
|   |-- carpark_test.py
|   `-- test_config.py
|-- checklist.md
|-- README.md
|-- LICENSE
`-- setup.py
```

## Getting started

1. Clone this repository to your machine.
2. Create a virtual environment and activate it.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install the project in editable mode if you want clean imports.

```bash
pip install -e .
```

## Running the application

```bash
cd smartpark
python3 no_pi.py
```

Two tkinter windows open. One is the public display showing the free bay
count, the temperature, and the current time. The other is a control window
that plays the role of the entry and exit sensors. Type a license plate, type
a temperature, then press the incoming or outgoing buttons to drive the
simulation.

## Running the tests

```bash
python3 -m unittest discover -s tests -p "*.py" -v
```

All eight tests should pass. The tests cover the configuration parser, entry
and exit bay counting, the zero capacity edge case, the unknown plate edge
case, and the temperature reading store.

## Configuration file

The CarPark loads its setup from `samples_and_snippets/config.json` by
default. A copy of the same shape lives at `smartpark/config.json` so the
config can travel with the code. The fields read by the application are
`name`, `location`, `total-spaces`, `broker` and `port`. The `Sensors` and
`Displays` lists are read so the application knows what hardware the lot is
expected to expose.

## Activity log

Every entry, exit, temperature reading, and rejected event is written to
`carpark_log.txt` in the current working directory. The file is created on
first write and appended thereafter. The log file gives the parking officer
an audit trail of every interaction with the carpark.
