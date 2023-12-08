import platformdirs


app_name = "petminion"
app_author = "geeksville"


def user_data_dir():
    """Get our data directory"""
    return platformdirs.user_data_dir(app_name, app_author, ensure_exists=True)


def user_cache_dir():
    """Get our cache directory"""
    return platformdirs.user_cache_dir(app_name, app_author, ensure_exists=True)
