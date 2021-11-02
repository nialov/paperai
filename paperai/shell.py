"""
paperai query shell module.
"""


from cmd import Cmd

from .models import Models
from .query import Query
from json import dumps


class Shell(Cmd):
    """
    paperai query shell.
    """

    def __init__(self, path):
        super(Shell, self).__init__()

        self.intro = "paperai query shell"
        self.prompt = "(paperai) "

        self.embeddings = None
        self.db = None
        self.path = path

    def preloop(self):
        # Load embeddings and questions.db
        self.embeddings, self.db = Models.load(self.path)

    def postloop(self):
        Models.close(self.db)

    def default(self, line):
        Query.query(self.embeddings, self.db, line, None, None)
