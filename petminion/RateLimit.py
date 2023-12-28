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

    @property
    def interval_secs(self) -> float:
        return state.interval_secs

    @property
    def is_runnable(self) -> bool:
        """
        Checks if a post can be made based on the last post time.  

        Returns:
            bool: True if a post can be made, False otherwise.
        """
        return time.time() - self.state.last_time >= self.state.interval_secs

    def set_ran(self):
        """
        Marks that we just did a rate-limited action.
        """
        self.state.last_time = time.time()
        save_state(self.state_name, self.state)

    def can_run(self) -> bool:
        """
        Checks if a post can be made based on the last post time.  If we can run we also mark that we ran.

        Returns:
            bool: True if a post can be made, False otherwise.
        """
        if self.is_runnable:
            self.set_ran()
            return True
        else:
            return False
