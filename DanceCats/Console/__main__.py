"""Main file for Console package."""

import os
from DanceCats.Console import manager


if os.environ.get('CONFIG_FILE'):
    app.config.from_envvar('CONFIG_FILE')
else:
    raise OSError(
        "Can't load configurations. Please specify configuration file"
    )

manager.run()
