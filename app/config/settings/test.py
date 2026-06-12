from .local import *  # noqa: F403

DATABASES["default"]["USER"] = "root"  # noqa: F405
DATABASES["default"]["PASSWORD"] = env("MYSQL_ROOT_PASSWORD")  # noqa: F405
DATABASES["default"]["TEST"] = {"NAME": "test_taeb"}  # noqa: F405
