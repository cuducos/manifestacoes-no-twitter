import typer

from manifestacoes.db import Mongo
from manifestacoes.to_csv import to_csv


app = typer.Typer()
db = Mongo()


@app.command()
def csv(file_name: str, compressed: bool = False):
    """Generates a CSV version of the dataset based on data from MongoDB. Uses
    LZMA if --compressed option is used."""
    to_csv(
        file_name,
        db.first_tweet.keys(),
        db.tweets,
        db.db.tweets.estimated_document_count(),
        compressed,
    )


if __name__ == "__main__":
    app()
