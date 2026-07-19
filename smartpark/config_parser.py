"""Helper to parse the json config file."""

import json


def parse_config(config_file):
    """Read the json file and return the carpark settings as a dict."""
    with open(config_file) as f:
        data = json.load(f)
    if "CarParks" in data:
        return data["CarParks"][0]
    return data


if __name__ == "__main__":
    cfg = parse_config("../samples_and_snippets/config.json")
    print(cfg)
