# coding: utf-8

from niamoto.testing import set_test_path
set_test_path()

if __name__ == "__main__":

    import sys
    import os
    import subprocess

    import sadisplay

    from niamoto.db import metadata

    PROJECT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    dot_destination_path = os.path.join(
        PROJECT_PATH,
        "docs",
        "_static",
        "db_schema.dot",
    )
    if len(sys.argv) > 1:
        dot_destination_path = sys.argv[1]

    desc = sadisplay.describe(
        [getattr(metadata, attr) for attr in dir(metadata)],
    )
    with open(dot_destination_path, 'w', encoding='utf-8') as f:
        f.write(sadisplay.dot(
            desc,
        ))

    svg_destination_path = os.path.join(
        PROJECT_PATH,
        "docs",
        "_static",
        "db_schema.svg",
    )

    if len(sys.argv) > 2:
        svg_destination_path = sys.argv[2]

    with open(svg_destination_path, 'w') as f:
        subprocess.Popen(
            ["dot", "-Tsvg", dot_destination_path],
            stdout=f
        )
