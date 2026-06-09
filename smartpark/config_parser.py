"""Configuration parser.

Reads the JSON configuration file and hands back the dictionary describing
the first carpark in the file. The file format and the helper are kept
separate from the CarPark class so the same parser can be reused by tests
and by any future tooling.
"""

import json
import os


def parse_config(config_file):
    """Parse the config file and return the carpark configuration dictionary.

    The parser is forgiving about two shapes:

    1. A flat object describing a single carpark.
    2. The richer shape used by the sample file that wraps the carpark inside
       a top level "CarParks" list. The first carpark in the list is returned.
    """
    with open(config_file, "r") as input_file:
        data = json.load(input_file)

    if isinstance(data, dict) and "CarParks" in data:
        return data["CarParks"][0]
    return data


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(here)
    sample_path = os.path.join(project_root, "samples_and_snippets", "config.json")
    config = parse_config(sample_path)
    print(config)
