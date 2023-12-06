#!python3

import argparse
import logging
# import os
import platformdirs
# import asyncio
from .Trainer import Trainer

"""The command line arguments"""
args = None


def main():
    """Perform command line steamback operations"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", "-d", help="Show debug log messages",
                        action="store_true")
    parser.add_argument("--test", "-t", help="Run integration code test",
                        action="store_true")
    parser.add_argument("--simulate", "-s", help="Simulate all hardware",
                        action="store_true")
    parser.add_argument("--daemon", "-D", help="Run as a daemon (headless, talks to cameras/devices but no GUI)",
                        action="store_true")

    global args
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    logger = logging.getLogger()
    logger.info(f'Petminion running...')

    app_name = "petminion"
    app_author = "geeksville"
    app_dir = platformdirs.user_data_dir(app_name, app_author)
    logger.info(f'Storing application data in { app_dir }')

    t = Trainer(args.simulate)

    if args.test:
        pass
        # asyncio.run(test.testImpl(e))
    elif args.daemon:
        pass
        # asyncio.run(d.run_forever())
    else:
        t.run()


if __name__ == "__main__":
    main()
