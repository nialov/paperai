"""
Command-line with typer.
"""
import logging
import warnings
from json import dumps
from pathlib import Path
from sqlite3 import Connection, Cursor
from typing import List, Optional, Tuple

import typer
from beartype import beartype
from nialog.logger import setup_module_logging
from rich.console import Console
from rich.pretty import pprint
from rich.table import Table
from txtai.embeddings import Embeddings

from paperai import utils

from .models import Models
from .query import Query

app = typer.Typer()


@app.callback()
def app_callback(
    logging_level: utils.LoggingLevel = typer.Option(utils.LoggingLevel.WARNING.value),
):
    """
    Use paperai to query articles.
    """
    # Ignore warning:
    # Trying to unpickle estimator TruncatedSVD from version 0.24.2 when using
    # version 1.0.1. This might lead to breaking code or invalid results. Use at
    # your own risk. For more info please refer to: #
    # https://scikit-learn.org/stable/modules/model_persistence.html
    # #security-maintainability-limitations
    warnings.filterwarnings(
        "ignore", message=".*Trying to unpickle.*", category=UserWarning
    )
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
    embeddings: Embeddings,
    cur: Cursor,
    query_text: str,
    n: int,
    threshold: Optional[float],
) -> List[Tuple[int, float, str, str]]:
    """
    Query search for best matches.
    """
    results = Query.search(embeddings, cur, query_text, n, threshold=threshold)
    return results


def rich_print(all_results: List[utils.QueryResults]):
    """
    Print result output with rich.
    """
    if len(all_results) == 0:
        return
    # sort results by score
    sorted_results = sorted(all_results, key=lambda result: result.score, reverse=True)
    column_names = ("text", "score", "title")
    table = Table(title="Query results", show_lines=True)

    for column_name in column_names:
        table.add_column(column_name)

    for result in sorted_results:
        table.add_row(
            *list(
                map(str, [getattr(result, column_name) for column_name in column_names])
            )
        )

    console = Console()

    console.print(table)


@beartype
def model_query(
    query_text: str,
    embeddings: Embeddings,
    db: Connection,
    n: int = 10,
    threshold: Optional[float] = None,
) -> List[utils.QueryResults]:
    """
    Query model for results.
    """
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
            "SELECT Title, Published, Publication, Design, Size, "
            "Sample, Method, Entry, Id, Reference FROM articles WHERE id = ?",
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
            query_results = utils.QueryResults(**full_result_dict)
            all_results.append(query_results)

    return all_results


@app.command()
def query_model(
    text: str = typer.Argument(""),
    model_path: Path = typer.Option(Models.modelPath(), dir_okay=True, exists=True),
    n: int = typer.Option(10),
    output_type: utils.OutputType = typer.Option(utils.OutputType.JSON.value),
    score_threshold: Optional[float] = typer.Option(None),
):
    """
    Query model.
    """
    argument_dict = dict(model_path=model_path, n=n, output_type=output_type)
    if len(text) == 0:
        logging.warning("Empty text argument.", extra=argument_dict)
        return
    embeddings, db = load_model(model_path=model_path)
    query_results = model_query(
        query_text=text,
        n=n,
        threshold=score_threshold,
        embeddings=embeddings,
        db=db,
    )

    if output_type == utils.OutputType.JSON:
        dictified = [result.__dict__ for result in query_results]
        pprint(dumps(dictified, indent=1))
    elif output_type == utils.OutputType.RICH:
        rich_print(query_results)


@app.command()
def preview_doi(
    doi: str = typer.Argument(""),
):
    """
    Preview doi.
    """
    if len(doi) == 0:
        print("Empty DOI.")
    print(doi)
