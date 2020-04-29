import lzma
from csv import DictWriter

from typer import progressbar


def to_csv(file_name, headers, rows, total=None, compressed=False):
    open_method = lzma.open if compressed else open
    with open_method(file_name, "wt") as fobj:
        writer = DictWriter(fobj, fieldnames=headers)
        writer.writeheader()

        kwargs = {"label": "Writing to CSV", "show_pos": True, "width": 0}
        if total:
            kwargs["length"] = total

        with progressbar(rows, **kwargs) as bar:
            for row in bar:
                writer.writerow(row)
