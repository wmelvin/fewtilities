import pytest

from pathlib import Path
from textwrap import dedent

import comment_links


def test_help(capsys):
    args = ["comment_links.py", "-h"]

    with pytest.raises(SystemExit):
        comment_links.main(args)

    captured = capsys.readouterr()

    assert "[-h]" in captured.out
    assert "comment_links.py (v." in captured.out


def test_opts(tmp_path):
    srctxt = tmp_path / "some.txt"
    srctxt.write_text("blah")
    outdir = str(tmp_path)
    args = [
        "comment_links.py",
        str(srctxt),
        "--output-dir",
        outdir,
    ]
    opts = comment_links.get_opts(args)
    assert str(srctxt) == str(opts.source_file)
    assert outdir == str(opts.out_file.parent)


def test_process_file(tmp_path):
    fake_script: Path = tmp_path / "fake.script"
    text = dedent(
        """
        # https://www.bogusoft.com/
        # A link at the top.

        # fake.script
        print("I am fake.")

        # Use SUMP instead.
        # https://www.bogusoft.com/

        print("blah")
        print("blah")
        print("blah")
        """
    )
    fake_script.write_text(text)

    args = ["comment_links.py", str(fake_script), "-o", str(tmp_path)]
    result = comment_links.main(args)
    assert result == 0

    files = list(tmp_path.glob("*.html"))
    assert len(files) == 1, "Should create one HTML file."
