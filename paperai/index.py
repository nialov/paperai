"""
Indexing module
"""

import os.path
import sqlite3
import sys

import regex as re
import yaml
from txtai.embeddings import Embeddings
from txtai.pipeline import Tokenizer

from .models import Models


class Index:
    """
    Methods to build a new sentence embeddings index.
    """

    # Section query and filtering logic constants
    SECTION_FILTER = r"background|(?<!.*?results.*?)discussion|introduction|reference"
    SECTION_QUERY = (
        "SELECT Id, Name, Text FROM sections "
        "WHERE (labels is null or labels NOT IN ('FRAGMENT', 'QUESTION'))"
    )

    @staticmethod
    def stream(dbfile, maxsize):
        """
        Stream documents from an articles.sqlite file.

        This method is a generator and will yield a row at time.

        Args:
            dbfile: input SQLite file
            maxsize: maximum number of documents to process
        """
        # Connection to database file
        db = sqlite3.connect(dbfile)
        cur = db.cursor()

        # Select tagged sentences without a NLP label. NLP labels are set for
        # non-informative sentences.
        query = Index.SECTION_QUERY + " AND tags is not null"

        if maxsize > 0:
            query += (
                " AND article in (SELECT id FROM articles ORDER BY entry DESC LIMIT %d)"
                % maxsize
            )

        # Run the query
        cur.execute(query)

        count = 0
        for row in cur:
            # Unpack row
            uid, name, text = row

            if not name or not re.search(Index.SECTION_FILTER, name.lower()):
                # Tokenize text
                tokens = Tokenizer.tokenize(text)

                document = (uid, tokens, None)

                count += 1
                if count % 1000 == 0:
                    print("Streamed %d documents" % (count), end="\r")

                # Skip documents with no tokens parsed
                if tokens:
                    yield document

        print("Iterated over %d total rows" % (count))

        # Free database resources
        db.close()

    @staticmethod
    def config(vectors):
        """
        Build embeddings configuration.

        Args:
            vectors: path to word vectors or configuration

        Returns:
            configuration
        """
        # Default vectors
        if not vectors:
            vectors = Models.vectorPath("cord19-300d.magnitude")

        # Read YAML index configuration
        if vectors.endswith(".yml"):
            with open(vectors, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)

        return {"path": vectors, "scoring": "bm25", "pca": 3, "quantize": True}

    @staticmethod
    def embeddings(dbfile, vectors, maxsize):
        """
        Build a sentence embeddings index.

        Args:
            dbfile: input SQLite file
            vectors: path to vectors file or configuration
            maxsize: maximum number of documents to process

        Returns:
            embeddings index
        """
        # Read config and create Embeddings instance
        embeddings = Embeddings(Index.config(vectors))

        # Build scoring index if scoring method provided
        if embeddings.config.get("scoring"):
            embeddings.score(Index.stream(dbfile, maxsize))

        # Build embeddings index
        embeddings.index(Index.stream(dbfile, maxsize))

        return embeddings

    @staticmethod
    def run(path, vectors, maxsize=0):
        """
        Execute an index run.

        Args:
            path: model path, if None uses default path
            vectors: path to vectors file or configuration, if None uses default path
            maxsize: maximum number of documents to process
        """
        # Default path if not provided
        if not path:
            path = Models.modelPath()

        dbfile = os.path.join(path, "articles.sqlite")

        print("Building new model")
        embeddings = Index.embeddings(dbfile, vectors, maxsize)
        embeddings.save(path)


if __name__ == "__main__":
    Index.run(
        sys.argv[1] if len(sys.argv) > 1 else None,
        sys.argv[2] if len(sys.argv) > 2 else None,
        int(sys.argv[3]) if len(sys.argv) > 3 else 0,
    )
