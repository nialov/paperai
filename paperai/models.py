"""
Models module
"""

import logging
import os
import os.path
import sqlite3
from pathlib import Path

from txtai.embeddings import Embeddings

ARTICLES_SQLITE_NAME = "articles.sqlite"
CONFIG_NAME = "config"


class Models:
    """
    Common methods for generating data paths.
    """

    @staticmethod
    def basePath(create=False):
        """
        Get base data path - ~/.cord19.

        Args:
            create: if directory should be created

        Returns:
            path
        """
        # Get model cache path
        path = os.path.join(os.path.expanduser("~"), ".cord19")

        # Create directory if required
        if create:
            os.makedirs(path, exist_ok=True)

        return path

    @staticmethod
    def modelPath(create=False):
        """
        Get model path for name.

        Args:
            create: if directory should be created

        Returns:
            path
        """
        path = os.path.join(Models.basePath(), "models")

        # Create directory if required
        if create:
            os.makedirs(path, exist_ok=True)

        return path

    @staticmethod
    def vectorPath(name, create=False):
        """
        Get vector path for name.

        Args:
            name: vectors name
            create: if directory should be created

        Returns:
            path
        """
        path = os.path.join(Models.basePath(), "vectors")

        # Create directory path if required
        if create:
            os.makedirs(path, exist_ok=True)

        # Append file name to path
        return os.path.join(path, name)

    @staticmethod
    def load(path):
        """
        Load an embeddings model and db database.

        Args:
            path: model path, if None uses default path

        Returns:
            (embeddings, db handle)
        """
        # Default path if not provided
        if not path:
            path = Models.modelPath()

        dbfile = os.path.join(path, "articles.sqlite")

        if os.path.isfile(os.path.join(path, "config")):
            logging.info(f"Loading model from {path}")
            embeddings = Embeddings()
            embeddings.load(path)
        else:
            embeddings = None

        # Connect to database file
        db = sqlite3.connect(dbfile)

        return (embeddings, db)

    @staticmethod
    def load_path(path: Path):
        """
        Load an embeddings model and db database.

        Args:
            path: model path, if None uses default path

        Returns:
            (embeddings, db handle)
        """
        if not path.is_dir():
            raise FileExistsError(
                f"Expected path to be a directory with {ARTICLES_SQLITE_NAME} file."
            )

        articles_path = path / ARTICLES_SQLITE_NAME
        config_path = path / CONFIG_NAME

        # dbfile = os.path.join(path, "articles.sqlite")

        # if os.path.isfile(os.path.join(path, "config")):
        if config_path.is_file():
            logging.info("Loading model from %s" % path)
            embeddings = Embeddings()
            embeddings.load(str(path))
        else:
            embeddings = None

        # Connect to database file
        db = sqlite3.connect(articles_path)

        return (embeddings, db)

    @staticmethod
    def close(db):
        """
        Close a SQLite database.

        Args:
            db: open database
        """
        # Free database resources
        db.close()
