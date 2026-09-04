"""Module entry point: `python -m fmea_agent demo examples/simple_pump.json`."""

import sys

from fmea_agent.cli.main import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
