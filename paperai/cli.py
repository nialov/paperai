"""
Command-line with typer.
"""
from .models import Models
from .query import Query
from typing import Dict, List, Tuple, Optional, Union
from json import dumps
from pathlib import Path
from beartype import beartype
import logging
import typer
from nialog.logger import setup_module_logging
from enum import Enum, unique
from txtai.embeddings import Embeddings
from sqlite3 import Connection, Cursor


@unique
class LoggingLevel(Enum):
    DEBUG = str(logging.DEBUG)
    INFO = str(logging.INFO)
    WARNING = str(logging.WARNING)
    ERROR = str(logging.ERROR)
    CRITICAL = str(logging.CRITICAL)


app = typer.Typer()


@app.callback()
def app_callback(
    logging_level: LoggingLevel = typer.Option(LoggingLevel.WARNING.value),
):
    setup_module_logging(logging_level_int=int(logging_level.value))


@beartype
def load_model(model_path: Path) -> Tuple[Embeddings, Connection]:
    """
    Load model from model_path.
    """
    embeddings, db = Models.load_path(model_path)
    if embeddings is None:
        logging.error(
            "No embeddings found for model.",
            extra=dict(model_path=model_path, db_connection=db),
        )
        raise ValueError("No embeddings found for model.")
    return embeddings, db


@beartype
def query_for_results(
        embeddings: Embeddings, cur: Cursor, query_text: str, n: int, threshold:Optional[float]
) -> List[Tuple[int, float, str, str]]:
    """
    Query search for best matches.
    """
    results = Query.search(embeddings, cur, query_text, n, threshold=threshold)
    return results


@beartype
def model_query(query_text: str, model_path: Path, n: int = 10, threshold:Optional[float] = None) -> List[Dict[str, Union[str, float]]]:
    """
    Query model for results.
    """
    embeddings, db = load_model(model_path=model_path)
    # Query.query(embeddings, db, line, None, None)

    cur = db.cursor()

    # Query for best matches
    results = query_for_results(embeddings, cur, query_text, n, threshold=threshold)

    # Get results grouped by document
    documents = Query.documents(results, n)

    all_results = []
    for uid in sorted(
        documents, key=lambda k: sum([x[0] for x in documents[k]]), reverse=True
    ):
        cur.execute(
            "SELECT Title, Published, Publication, Design, Size, Sample, Method, Entry, Id, Reference FROM articles WHERE id = ?",
            [uid],
        )
        article = cur.fetchone()
        query_result_dict = {
            "title": article[0],
            "published": Query.date(article[1]),
            "publication": article[2],
            "entry": article[7],
            "id": article[8],
            "reference": article[9],
        }
        for document_match in documents[uid]:
            score, text = document_match
            scoring_result_dict = {"score": score, "text": text}
            full_result_dict = {**scoring_result_dict, **query_result_dict}
            all_results.append(full_result_dict)

    return all_results


@app.command()
def query_model(
    text: str = typer.Argument(""),
    model_path: Path = typer.Option(Models.modelPath(), dir_okay=True, exists=True),
    n: int = typer.Option(10),
    json_output: bool = typer.Option(True),
    score_threshold:Optional[float] = typer.Option(None),
):
    argument_dict = dict(model_path=model_path, n=n, json_output=json_output)
    if len(text) == 0:
        logging.warning("Empty text argument.", extra=argument_dict)
        return
    query_results = model_query(query_text=text, model_path=model_path, n=n, threshold=score_threshold)

    if json_output:
        typer.echo(dumps(query_results))


@app.command()
def preview_doi(
    doi: str = typer.Argument(""),
):
    if len(doi) == 0:
        print("Empty DOI.")
    print(doi)
