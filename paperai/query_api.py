"""
FastAPI entrypoint.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from sqlite3 import Connection
from typing import Optional

from fastapi import FastAPI
from txtai.embeddings import Embeddings

from paperai import cli, models

app = FastAPI()


@dataclass
class LoadedModel:

    """
    Container class for loaded model db and embeddings.
    """

    db: Optional[Connection] = None
    embeddings: Optional[Embeddings] = None


LOADED_MODEL = LoadedModel()


@app.get("/")
async def root():
    """
    Root get entrypoint.
    """
    return {"Text": "Welcome to paperai API."}


@app.get("/query/{query_text}")
async def query(query_text: str):
    """
    Query get entrypoint.
    """
    if LOADED_MODEL.db is None:
        assert LOADED_MODEL.embeddings is None
        embeddings, db = cli.load_model(model_path=Path(models.Models.modelPath()))
        LOADED_MODEL.embeddings = embeddings
        LOADED_MODEL.db = db
    else:
        embeddings, db = LOADED_MODEL.embeddings, LOADED_MODEL.db
    try:
        assert db is not None
        assert embeddings is not None
        query_results = cli.model_query(
            query_text=query_text, embeddings=embeddings, db=db
        )
    except ValueError:
        logging.error(
            "Failed to query model.", exc_info=True, extra=dict(query_text=query_text)
        )
        return {"Error": "Failed to query model."}
    query_results_json = [result.__dict__ for result in query_results]
    return query_results_json
