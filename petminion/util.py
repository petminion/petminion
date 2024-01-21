import configparser
import logging
import os

import jsonpickle
import platformdirs

app_name = "petminion"
app_author = "geeksville"
logger = logging.getLogger()


def has_windows() -> bool:
    """Return true if we are running on a system with XWindows"""
    return os.environ.get("DISPLAY", None) is not None


def user_data_dir() -> str:
    """Get our data directory"""
    return platformdirs.user_data_dir(app_name, app_author, ensure_exists=True)


def user_cache_dir() -> str:
    """Get our cache directory"""
    return platformdirs.user_cache_dir(app_name, app_author, ensure_exists=True)


def user_config_dir() -> str:
    """Get our config directory"""
    return platformdirs.user_config_dir(app_name, app_author, ensure_exists=True)


def user_state_dir() -> str:
    """Get our state directory"""
    return platformdirs.user_state_dir(app_name, app_author, ensure_exists=True)


def save_state(file_base_name: str, data: any) -> None:
    """Save an object's state using jsonpickle"""
    path = os.path.join(user_state_dir(), file_base_name + ".json")
    # logger.debug(f'Saving state to {path}')
    json = jsonpickle.encode(data, indent=2)
    with open(path, "w") as f:
        f.write(json)


# set to true to disable state loading during unit tests
global state_loading_disabled
state_loading_disabled = False


def load_state(file_base_name: str, default_value: any = None) -> any:
    """
    Load an object's state using jsonpickle.

    Args:
        file_base_name (str): The base name of the file to load the state from.
        default_value (any, optional): The default value to return if loading the state fails. Defaults to None.

    Returns:
        any: The loaded object's state.

    Raises:
        Exception: If loading the state fails and no default value is provided.
    """
    try:
        if state_loading_disabled:
            logger.debug(f'State loading disabled for {file_base_name}')
            if default_value:
                return default_value
            raise Exception("State loading disabled for unit tests")

        path = os.path.join(user_state_dir(), file_base_name + ".json")
        logger.debug(f'Loading state from {path}')
        with open(path, "r") as f:
            json = f.read()
            r = jsonpickle.decode(json)
            if isinstance(r, dict):
                # something changed in the representation so jsonpickle punted and gave us a dict
                raise Exception("Serialization changed, saved contents ignored")
            return r
    except Exception as e:
        if default_value:
            logger.warning(f'Failed to load state from {path}, using defaults...')
            return default_value
        else:
            raise e


class AppConfig:
    """Provides read/write access to application config file"""

    def __init__(self) -> None:
        """
        Initializes an instance of MyClass.

        This method sets up the filename, logger, and configuration for the class.
        It reads the application settings from the config.ini file and sets defaults if necessary.
        """
        self.filename = filename = os.path.join(
            user_config_dir(), "config.ini")
        logger.info(
            f"Reading application settings from {filename} - you can edit this file to change options.")
        self.config = config = configparser.ConfigParser()

        self.set_defaults()
        config['settings'] = {}  # default 'settings' if not found in file
        if not os.path.exists(filename):
            self.save()  # use defaults to init the file on the disk
        else:
            config.read(filename)
            # always reset the defaults because they might have changed in development
            self.set_defaults()

    def set_defaults(self) -> None:
        """
        Sets the default configuration values for the PetMinion class.

        This method initializes the 'DEFAULT' section of the configuration dictionary
        with default values for various settings such as 'MQTTHost', 'Feeder', 'Camera',
        'TrainingRule', 'FastModel', and 'SimFallback'.

        Note:
            If this class is reused in the future, it is recommended to move the default
            configuration values to a separate location.

        """
        self.config['DEFAULT'] = {
            'MQTTHost': 'localhost',
            'Feeder': 'ZigbeeFeeder',
            'Camera': 'CV2Camera',
            'TrainingRule': 'SimpleFeederRule',
            'FastModel': False,
            'SimFallback': True,
            'SimSocialMedia': False
        }

    @property
    def settings(self) -> configparser.SectionProxy:
        """Return the first customized set of settings"""
        return self.config['settings']

    def save(self) -> None:
        """Store a (possibly modified config) to the filesystem"""
        with open(self.filename, 'w') as f:
            self.config.write(f)


app_config = AppConfig()
