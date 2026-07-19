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

## Activity log

Every entry, exit, temperature reading, and rejected event is written to
`carpark_log.txt` in the current working directory. The file is created on
first write and appended thereafter. The log file gives the parking officer
an audit trail of every interaction with the carpark.
