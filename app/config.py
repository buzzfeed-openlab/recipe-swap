import os

# if config_vars_secret.py exists, use that for the settings
if os.path.isfile(os.path.dirname(__file__)+'/config_vars_secret.py'):
    from .config_vars_secret import CONFIG_VARS

# otherwise, look at env vars for config variables
# (this is for cases where it's easier to set env vars than add a file, e.g. if deploying with docker)
else:
    CONFIG_VARS = {
        "DB_USER" : os.getenv('DB_USER', 'root'),
        "DB_PW" :  os.getenv('DB_PW', ''),
        "DB_HOST" : os.getenv('DB_HOST', 'localhost'),
        "DB_NAME" : os.getenv('DB_NAME', 'random_recipes'),

        "ADMIN_USER" : os.getenv('ADMIN_USER', 'admin'),
        "ADMIN_PASS" : os.getenv('ADMIN_PASS', 'something-secret'),

        "SECRET_KEY" : os.getenv('SECRET_KEY', 'another-secret-thing'),

        "DEBUG" : os.getenv('DEBUG', 'False')
    }
