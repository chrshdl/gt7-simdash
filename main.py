#!/usr/bin/env python3
import argparse
import json
from dash import Dash


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="PS5 sim dash")
  parser.add_argument("--config", help="json with the config", default="config.json")
  args = parser.parse_args()

  with open(args.config, 'r') as fid:
    config = json.load(fid)

  dash = Dash(config)
  dash.run()

