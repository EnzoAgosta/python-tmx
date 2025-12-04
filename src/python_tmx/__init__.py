import warnings

warnings.warn(
    "python-tmx has been renamed to 'hypomnema'. Install 'hypomnema' and use 'import hypomnema as hm'.",
    DeprecationWarning,
    stacklevel=2,
)

from hypomnema import *  # noqa: F403, E402
