from itertools import repeat, chain
from pathlib import Path
import shutil
import os

from docutils.core import publish_file


def walk_files(*args, **kwargs):
    return chain.from_iterable(
        (Path(dirpath) / filename for filename in filenames)
        for dirpath, _, filenames in os.walk(*args, **kwargs)
    )


def render_source(source_path, *, base_path, build_path):
    sp = source_path.relative_to(base_path)
    destination_path = build_path / sp.parent / sp.with_suffix('').name / "index.html"

    os.makedirs(destination_path.parent, exist_ok=True)
    print(f"rendering {source_path=!s} to {destination_path=!s}")
    publish_file(
        writer_name='html5',
        source_path=source_path,
        destination_path=destination_path,
        settings_overrides=dict(
            stylesheet_path='./static/css/bluespan-normalize.css',
            template='./static/template/mobile.tmpl',
        )
    )


def render_all():
    base_path = Path("./source")
    build_path = Path("./build")
    for path in walk_files(base_path):
        render_source(path, base_path=base_path, build_path=build_path)


def copy_static():
    print(f"copying ./static to ./build/static")
    shutil.copytree("./static", "./build/static", dirs_exist_ok=True)


def main():
    render_all()
    copy_static()


if __name__ == "__main__":
    main()
