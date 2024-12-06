from __future__ import annotations

import os
from pathlib import Path

import pytest

import scren


@pytest.fixture()
def make_test_files(tmp_path: Path):
    """ Create test files for scren.py.
    """
    dir_path = tmp_path / "Pictures"
    dir_path.mkdir()

    file_list: list[Path] = []
    name_list: list[str] = []

    #  Pattern 1:

    file_list.append(dir_path / "Screenshot_from_2022-02-03_17-31-01.png")
    name_list.append("screen_20220203_173101.png")

    file_list.append(dir_path / "Screenshot from 2022-02-24 14-20-02.png")
    name_list.append("screen_20220224_142002.png")

    file_list.append(dir_path / "Screenshot_from_2022-03-22_07-59-03-crop.jpg")
    name_list.append("screen_20220322_075903.jpg")

    file_list.append(dir_path / "Screenshot at 2022-04-12 09-10-04.png")
    name_list.append("screen_20220412_091004.png")

    file_list.append(dir_path / "Screenshot_2023-03-01_07-08-05.png")
    name_list.append("screen_20230301_070805.png")

    #  Pattern 2:

    file_list.append(dir_path / "Screenshot_20240301_070806.png")
    name_list.append("screen_20240301_070806.png")

    for f in file_list:
        f.write_bytes(b"0")
        assert f.exists()

    return (dir_path, file_list, name_list)


@pytest.mark.parametrize("move_arg", ["-m", "--move-now"])
def test_scren_whatif(make_test_files, move_arg):
    d, files, _ = make_test_files
    os.chdir(d)
    assert str(Path.cwd()) == str(d)

    # Should not move files when the --what-if argument is passed.
    args = ["--what-if"]
    scren.main(args)
    assert all(f.exists() for f in files)

    # Should not move files when the --what-if and "-m" arguments are passed.
    args = ["--what-if", move_arg]
    scren.main(args)
    assert all(f.exists() for f in files)


@pytest.mark.parametrize("move_arg", ["-m", "--move-now"])
def test_scren(make_test_files, move_arg):
    d, files, names = make_test_files
    os.chdir(d)
    assert str(Path.cwd()) == str(d)

    args = [move_arg]
    scren.main(args)

    # Should move (rename) files when -m argument is passed.
    assert all(not f.exists() for f in files)
    assert len(list(d.glob("screen_*"))) == len(files)
    assert all(d.joinpath(nm).exists() for nm in names)


def test_scren_bymo(make_test_files):
    d, files, names = make_test_files
    os.chdir(d)
    assert str(Path.cwd()) == str(d)

    args = ["-m", "--by-mo"]
    scren.main(args)

    # Should move files to monthly dirs when --by-mo argument is passed.
    assert all(not f.exists() for f in files)
    assert len(list(d.glob("**/screen_*"))) == len(files)

    # By month dirs should be created based on the year and month in the new file name,
    # not the file modified time. The dir should be named as "YYYY_MM".
    for nm in names:
        mo_dir = d.joinpath(nm[7:11] + "_" + nm[11:13])
        assert mo_dir.exists()
        assert mo_dir.joinpath(nm).exists()


def test_scren_user_input_n(make_test_files, monkeypatch):
    def fake_input_n(prompt):
        return "n"

    monkeypatch.setattr(scren, "get_input_lower", fake_input_n)

    d, files, _ = make_test_files
    os.chdir(d)
    assert str(Path.cwd()) == str(d)

    args = []
    scren.main(args)

    #  Should not move (rename) files when user input is 'n'.
    assert all(f.exists() for f in files)


def test_scren_user_input_y(make_test_files, monkeypatch):
    def fake_input_y(prompt):
        return "y"

    monkeypatch.setattr(scren, "get_input_lower", fake_input_y)

    d, files, names = make_test_files
    os.chdir(d)
    assert str(Path.cwd()) == str(d)

    args = []
    scren.main(args)

    # Should move (rename) files when user input is "y".
    assert all(not f.exists() for f in files)
    assert len(list(d.glob("screen_*"))) == len(files)
    assert all(d.joinpath(nm).exists() for nm in names)


def test_scren_user_input_enter(make_test_files, monkeypatch):
    def fake_input_enter(prompt):
        return ""

    monkeypatch.setattr(scren, "get_input_lower", fake_input_enter)

    d, files, names = make_test_files
    os.chdir(d)
    assert str(Path.cwd()) == str(d)

    args = []
    scren.main(args)

    # Should move (rename) files when user input default is "y".
    assert all(not f.exists() for f in files)
    assert len(list(d.glob("screen_*"))) == len(files)
    assert all(d.joinpath(nm).exists() for nm in names)
