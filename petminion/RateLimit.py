import time
from functools import cached_property

from .util import load_state, save_state


class SavedState:
    def __init__(self, interval_secs: float):
        self.interval_secs = interval_secs
        self.last_time = 0.0


class SimpleLimit:
    """
    A class to implement rate limiting functionality. No serialization is supported for this basic class.
    """

    def __init__(self, interval_secs: float):
        """
        Initializes the SimpleLimit object. 
        """
        self._interval_secs = interval_secs

    @cached_property
    def state(self) -> SavedState:
        """We use a cached property so the actual load of state doesn't happen until _after_ any globals are created.  This allows
        unit tests to disable state loading before the globals are created.
        """
        return SavedState(self._interval_secs)

    @property
    def interval_secs(self) -> float:
        return self.state.interval_secs

    @interval_secs.setter
    def interval_secs(self, value: float):
        self.state.interval_secs = value

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


class RateLimit(SimpleLimit):
    """
    A class to implement rate limiting functionality. We serialize state to disk so limits are respected across restarts.
    """

    def __init__(self, state_name: str, interval_secs: float):
        """
        Initializes the RateLimit object. 
        """
        super().__init__(interval_secs)
        self.state_name = state_name

    # override to add serialization
    @cached_property
    def state(self) -> SavedState:
        """We use a cached property so the actual load of state doesn't happen until _after_ any globals are created.  This allows
        unit tests to disable state loading before the globals are created.
        """
        return load_state(self.state_name, SavedState(self._interval_secs))

    def set_ran(self):
        """
        Marks that we just did a rate-limited action.
        """
        super().set_ran()
        save_state(self.state_name, self.state)
