"""
Utils module
"""

import hashlib
from pathlib import Path


class Utils:
    """
    Utility constants and methods
    """

    PATH = "/tmp/paperai"
    DBFILE = PATH + "/articles.sqlite"
    VECTORFILE = PATH + "/vectors.magnitude"

    @staticmethod
    def hashfile(path):
        """
        Builds a MD5 hash for file at path.

        Args:
            path: full path to file

        Returns:
            MD5 hash
        """

        with open(path, "r") as data:
            # Read file into string and build MD5 hash
            return hashlib.md5(data.read().encode()).hexdigest()


TEST_DIR_PATH = Path(Utils.PATH)

if (not TEST_DIR_PATH.exists()) and (not TEST_DIR_PATH.is_dir()):
    raise FileNotFoundError(
        f"Expected test data dir to exist at {TEST_DIR_PATH}.\n"
        "Run:\n    make data\nto install needed test data."
    )
