import datetime
import logging
import textwrap
from typing import Any
from unittest.mock import patch

import pytest
from freezegun import freeze_time

# Must be before importint petminion
from petminion import BallRecognizer, Feeder, ImageRecognizer, Trainer, util
from petminion.Recognizer import ImageDetection


def patch_detections(seen_names: list[str]) -> Any:
    """Simulate the named objects being seen."""
    detections = [ImageDetection(name) for name in seen_names]
    return patch.object(ImageRecognizer.ImageRecognizer, 'do_detection', return_value=(None, detections))


def patch_balls(seen_names: list[str]) -> Any:
    """Simulate the named objects being seen."""
    detections = [ImageDetection(name) for name in seen_names]
    return patch.object(BallRecognizer.BallRecognizer, 'do_detection', return_value=(None, detections))


@pytest.mark.integtest
def test_simple_feeder_rule(config_for_testing) -> None:
    """A basic test of the entire app (using simulated data)
    """
    with freeze_time("2022-01-01 06:00:00") as ft:
        # logging.basicConfig(level=logging.DEBUG if True else logging.INFO)
        # logger = logging.getLogger()
        # logger.info('Petminion integration test running...')

        # make sure we load the simple feeder rule
        util.app_config.config.read_string(textwrap.dedent("""
            [settings]
            trainingrule = SimpleFeederRule
            """))

        trainer = Trainer(is_simulated=True)

        def tick(delta=datetime.timedelta(seconds=1)):
            ft.tick(delta)
            trainer.run_once()

        with patch.object(Feeder.Feeder, 'feed') as mock_feeder:
            # Simulate a cat being detected
            with patch_detections(["cat"]):
                tick()

                # verify feeding didn't happen (because too early)
                mock_feeder.assert_not_called()

                tick(datetime.timedelta(minutes=61))
                # verify feeding happened (because right time and cat visible)
                mock_feeder.assert_called_once()
                mock_feeder.reset_mock()

                tick()

                # verify feeding didn't happen (too soon)
                mock_feeder.assert_not_called()
                mock_feeder.reset_mock()

                # wait 15 mins and now it should feed again
                tick(datetime.timedelta(minutes=15))

                mock_feeder.assert_called_once()


@pytest.mark.integtest
def test_token_trainer_rule(config_for_testing) -> None:
    """A basic test of the entire app (using simulated data)
    """
    with freeze_time("2022-01-01 06:00:00") as ft:
        # logging.basicConfig(level=logging.DEBUG if True else logging.INFO)
        # logger = logging.getLogger()
        # logger.info('Petminion integration test running...')

        # make sure we load the simple feeder rule
        util.app_config.config.read_string(textwrap.dedent("""
            [settings]
            trainingrule = TokenTrainer
            """))

        trainer = Trainer(is_simulated=True)

        def tick(delta=datetime.timedelta(seconds=1)):
            ft.tick(delta)
            trainer.run_once()

        with patch.object(Feeder.Feeder, 'feed') as mock_feeder:
            # Simulate a cat being detected
            with patch_detections(["cat"]):
                with patch_balls(["ball"]):
                    tick()

                    # verify feeding didn't happen (because too early)
                    mock_feeder.assert_not_called()

                    tick(datetime.timedelta(minutes=61))
                    # verify feeding happened (because right time and cat visible)
                    mock_feeder.assert_called_once()
                    mock_feeder.reset_mock()

                    # now add a second ball to the scene
                    with patch_balls(["ball", "ball"]):
                        tick()

                        # verify feeding didn't happen (too soon)
                        mock_feeder.assert_not_called()
                        mock_feeder.reset_mock()

                        # wait 3 mins and now it should feed again (after the 1 min timeout)
                        tick(datetime.timedelta(minutes=3))

                        mock_feeder.assert_called_once()
