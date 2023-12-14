#!python3

import argparse
import logging
import os
import sys
from .Trainer import Trainer
from .util import app_config, user_data_dir

"""The command line arguments"""
args = None


def init_logging():
    """Setup our logging environment"""

    rootLogger = logging.getLogger()

    filename = os.path.join(user_data_dir(), "petminion.log")
    fileHandler = logging.FileHandler(filename)

    fileFormatter = logging.Formatter(
        "%(asctime)s %(levelname)-5.5s %(message)s")
    fileHandler.setFormatter(fileFormatter)
    rootLogger.addHandler(fileHandler)

    # [%(threadName)-12.12s]
    consoleFormatter = logging.Formatter(
        "%(asctime)s %(levelname)-5.5s %(message)s", "%H:%M:%S")
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(consoleFormatter)
    rootLogger.addHandler(consoleHandler)


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

    init_logging()
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)
    logger.info(f'Petminion running...')

    if not os.path.exists("/dev/video0") and app_config.settings['SimFallback']:
        logger.warning(
            f'No camera detected, forcing simulation mode instead...')
        args.simulate = True

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
