import time

from petminion.rate_limit import RateLimit


def test_can_post_when_interval_not_passed():
    r = RateLimit("test_state", 5)
    assert r.can_run()  # set last_time
    time.sleep(1)
    assert not r.can_run()
