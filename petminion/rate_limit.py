import time
from typing import NamedTuple

from .util import load_state, save_state


class SavedState:
    def __init__(self, interval_secs: float):
        self.interval_secs = interval_secs
        self.last_time = 0.0


class RateLimit:
    """
    A class to implement rate limiting functionality.
    """

    def __init__(self, state_name: str, interval_secs: float):
        """
        Initializes the RateLimit object.
        """
        self.state_name = state_name
        self.state = load_state(state_name, SavedState(interval_secs))

    def can_run(self) -> bool:
        """
        Checks if a post can be made based on the last post time.

        Returns:
            bool: True if a post can be made, False otherwise.
        """
        if time.time() - self.state.last_time >= self.state.interval_secs:
            self.state.last_time = time.time()
            save_state(self.state_name, self.state)
            return True
        else:
            return False
