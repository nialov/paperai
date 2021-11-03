"""
paperai query shell module.
"""


from cmd import Cmd

from .models import Models
from .query import Query


class Shell(Cmd):
    """
    paperai query shell.
    """

    def __init__(self, path):
        """
        Initialize Shell.
        """
        super().__init__()

        self.intro = "paperai query shell"
        self.prompt = "(paperai) "

        self.embeddings = None
        self.db = None
        self.path = path

    def preloop(self):
        """
        Do things before loop.
        """
        # Load embeddings and questions.db
        self.embeddings, self.db = Models.load(self.path)

    def postloop(self):
        """
        Do things after loop.
        """
        Models.close(self.db)

    def default(self, line):
        """
        Do default action.
        """
        Query.query(self.embeddings, self.db, line, None, None)
