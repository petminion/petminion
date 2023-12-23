import platformdirs
import configparser
import logging
import os

app_name = "petminion"
app_author = "geeksville"
logger = logging.getLogger()


def user_data_dir():
    """Get our data directory"""
    return platformdirs.user_data_dir(app_name, app_author, ensure_exists=True)


def user_cache_dir():
    """Get our cache directory"""
    return platformdirs.user_cache_dir(app_name, app_author, ensure_exists=True)


def user_config_dir():
    """Get our config directory"""
    return platformdirs.user_config_dir(app_name, app_author, ensure_exists=True)


def user_state_dir():
    """Get our state directory"""
    return platformdirs.user_state_dir(app_name, app_author, ensure_exists=True)


class AppConfig:
    """Provides read/write access to application config file"""

    def __init__(self):
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
        config['settings'] = {}
        if not os.path.exists(filename):
            self.save()
        else:
            config.read(filename)
            # always reset the defaults because they might have changed in development
            self.set_defaults()

    def set_defaults(self):
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
            'SimFallback': True
        }

    @property
    def settings(self):
        """Return the first customized set of settings"""
        return self.config['settings']

    def save(self):
        """Store a (possibly modified config) to the filesystem"""
        with open(self.filename, 'w') as f:
            self.config.write(f)


app_config = AppConfig()
