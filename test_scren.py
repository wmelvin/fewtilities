from pathlib import Path
from typing import List

import os
import pytest

import scren


@pytest.fixture()
def make_test_files(tmp_path: Path):
    dir_path = tmp_path / "Pictures"
    dir_path.mkdir()

    file_list: List[Path] = []

    #  Pattern 1:
    file_list.append(dir_path / "Screenshot_from_2022-02-03_17-31-01.png")
    file_list.append(dir_path / "Screenshot from 2022-02-24 14-20-02.png")
    file_list.append(dir_path / "Screenshot_from_2022-02-22_07-59-03-crop.jpg")
    file_list.append(dir_path / "Screenshot at 2022-02-12 09-10-04.png")
    file_list.append(dir_path / "Screenshot_2022-03-01_07-08-05.png")

    #  Pattern 2:
    file_list.append(dir_path / "Screenshot_20220301_070806.png")

    for f in file_list:
        f.write_bytes(b"0")
        assert f.exists()

    return (dir_path, file_list)


def test_scren(make_test_files):
    d, files = make_test_files
    os.chdir(d)
    assert str(Path.cwd()) == str(d)

    args = ["scren.py", "--what-if"]
    scren.main(args)

    # Should not move files when the --what-if argument is passed.
    assert all(f.exists() for f in files)

    args = ["scren.py", "-m"]
    scren.main(args)

    # Should move (rename) files when -m argument is passed.
    assert all(not f.exists() for f in files)

    assert len(list(d.glob("screen_*"))) == len(files)


def test_scren_user_input_n(make_test_files, monkeypatch):
    def fake_user_input_n(prompt, choices, default):
        return "n"

    monkeypatch.setattr(scren, "get_user_input", fake_user_input_n)

    d, files = make_test_files
    os.chdir(d)
    assert str(Path.cwd()) == str(d)

    args = ["scren.py"]
    scren.main(args)

    #  Should not move (rename) files when user input is 'n'.
    assert all(f.exists() for f in files)


def test_scren_user_input_y(make_test_files, monkeypatch):
    def fake_user_input_y(prompt, choices, default):
        return "y"

    monkeypatch.setattr(scren, "get_user_input", fake_user_input_y)

    d, files = make_test_files
    os.chdir(d)
    assert str(Path.cwd()) == str(d)

    args = ["scren.py"]
    scren.main(args)

    # Should move (rename) files when user input is "y".
    assert all(not f.exists() for f in files)

    assert len(list(d.glob("screen_*"))) == len(files)
