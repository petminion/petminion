import datetime
import logging
from unittest.mock import patch

import pytest
from freezegun import freeze_time

# Must be before importint petminion
from petminion import Feeder, ImageRecognizer, Trainer, util
from petminion.Recognizer import ImageDetection


@pytest.mark.integtest
def test_integration():
    """A basic test of the entire app (using simulated data)
    """
    util.state_loading_disabled = True  # make tests not use saved state files

    with freeze_time("2022-01-01 06:00:00") as ft:
        logging.basicConfig(level=logging.DEBUG if True else logging.INFO)
        logger = logging.getLogger()
        logger.info('Petminion integration test running...')

        trainer = Trainer(is_simulated=True)

        def tick(delta=datetime.timedelta(seconds=1)):
            ft.tick(delta)
            trainer.run_once()

        with patch.object(Feeder.Feeder, 'feed') as mock_feeder:
            # Simulate a cat being detected
            with patch.object(ImageRecognizer.ImageRecognizer, 'do_detection', return_value=(None, [ImageDetection("cat")])) as mock_detection:
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
