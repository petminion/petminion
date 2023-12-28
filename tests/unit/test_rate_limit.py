import time

from petminion.RateLimit import RateLimit


def test_rate_limit():
    r = RateLimit("test_state", 5)
    assert r.can_run()  # set last_time
    time.sleep(1)
    assert not r.can_run()
