"""
FastAPI entrypoint.
"""

from fastapi import FastAPI
from paperai import cli, models
from pathlib import Path
import logging
from dataclasses import dataclass
from sqlite3 import Connection
from txtai.embeddings import Embeddings
from typing import  Optional

app = FastAPI()

@dataclass
class LoadedModel:
    db: Optional[Connection] = None
    embeddings: Optional[Embeddings] = None

LOADED_MODEL = LoadedModel()


@app.get("/")
async def root():
    return {"Text": "Welcome to paperai API."}

@app.get("/query/{query_text}")
async def query(query_text:str):
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
        query_results = cli.model_query(query_text=query_text, embeddings=embeddings, db=db)
    except ValueError:
        logging.error("Failed to query model.", exc_info=True, extra=dict(query_text=query_text))
        return {"Error": "Failed to query model."}
    query_results_json = [result.__dict__ for result in query_results]
    return query_results_json


