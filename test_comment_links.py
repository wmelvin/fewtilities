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


def test_file_not_found(capsys, tmp_path):
    file_name = str(tmp_path / "NotHere")

    args = ["comment_links.py", file_name]

    with pytest.raises(SystemExit):
        comment_links.main(args)

    captured = capsys.readouterr()
    assert "Cannot find file" in captured.err
    assert file_name in captured.err


def test_outdir_not_found(capsys, tmp_path):
    file_path = tmp_path / "HereIAm.txt"
    file_path.write_text("hi")
    dir_name = str(tmp_path / "NotHere")

    args = ["comment_links.py", str(file_path), "-o", dir_name]

    with pytest.raises(SystemExit):
        comment_links.main(args)

    captured = capsys.readouterr()
    assert "Cannot find directory" in captured.err
    assert dir_name in captured.err


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
    assert str(srctxt) == str(opts.source_files[0])
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


def test_process_two_files(tmp_path):
    fake_script_1: Path = tmp_path / "fake-1.script"
    fake_script_2: Path = tmp_path / "fake-2.script"
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
    fake_script_1.write_text(text)
    fake_script_2.write_text(text)

    args = [
        "comment_links.py",
        str(fake_script_1),
        str(fake_script_2),
        "-o",
        str(tmp_path),
        "--no-dt"
    ]
    result = comment_links.main(args)
    assert result == 0

    files = list(tmp_path.glob("*.html"))
    assert len(files) == 1, "Should create one HTML file."

    out_file = tmp_path / "comment_links.html"
    assert out_file.exists()

    out_text = out_file.read_text()
    assert fake_script_1.name in out_text
    assert fake_script_2.name in out_text
