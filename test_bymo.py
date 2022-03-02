from datetime import datetime, timedelta
from pathlib import Path

import os

import bymo


def make_test_file(
    dir_path: Path, file_name: str, time_stamp: datetime.timestamp
):
    f = dir_path / file_name
    f.write_text(f.name)
    assert f.exists()
    os.utime(f, (time_stamp, time_stamp))
    assert f.stat().st_mtime == time_stamp
    return f


def make_test_files(dir_path: Path, base_dt: datetime):
    t1 = base_dt
    f1 = make_test_file(dir_path, "file-1.txt", t1.timestamp())

    t2 = base_dt - timedelta(days=30)
    f2 = make_test_file(dir_path, "file-2.ini", t2.timestamp())
    f3 = make_test_file(dir_path, "file-3.opt", t2.timestamp())

    t4 = base_dt - timedelta(days=60)
    f4 = make_test_file(dir_path, "file-4.txt", t4.timestamp())

    return [f1, f2, f3, f4]


def mo_dir(file_path: Path):
    """Returns the directory name for the month of the given file's mtime."""
    s = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y_%m")
    return s


def test_does_not_move_files_wo_arg_m(tmp_path: Path):
    d = tmp_path / "files"
    print(f"tmp_path: {d}")
    d.mkdir()
    test_dt = datetime.fromisoformat("2022-02-14")
    files = make_test_files(d, test_dt)
    targets = [Path(d / mo_dir(f) / f.name) for f in files]

    os.chdir(d)
    assert str(Path.cwd()) == str(d)

    args = ["bymo.py"]
    bymo.main(args)

    # Should not move files when -m argument is not passed.
    assert all(f.exists() for f in files)
    assert all(not f.exists() for f in targets)


def test_moves_all_files_w_only_arg_m(tmp_path: Path):
    d = tmp_path / "files"
    d.mkdir()
    test_dt = datetime.fromisoformat("2022-02-14")
    files = make_test_files(d, test_dt)
    targets = [Path(d / mo_dir(f) / f.name) for f in files]

    os.chdir(d)
    assert str(Path.cwd()) == str(d)

    args = ["bymo.py", "-m"]
    bymo.main(args)

    # Should move all files when only -m argument is passed.
    assert all(not f.exists() for f in files)

    assert (d / "2021_12").exists()
    assert (d / "2022_01").exists()
    assert (d / "2022_02").exists()

    assert all(f.exists() for f in targets)


def test_moves_only_specified_files(tmp_path: Path):
    d = tmp_path / "files"
    print(f"tmp_path: {d}")
    d.mkdir()
    test_dt = datetime.fromisoformat("2022-02-14")
    files = make_test_files(d, test_dt)
    targets = [Path(d / mo_dir(f) / f.name) for f in files]

    os.chdir(d)
    assert str(Path.cwd()) == str(d)

    args = ["bymo.py", "-m", "*.txt"]
    bymo.main(args)

    # Should move only specified files when -m argument is also passed.
    assert all(f.exists() for f in files if f.suffix == ".ini")
    assert all(not f.exists() for f in files if f.suffix == ".txt")

    assert (d / "2021_12").exists()
    assert not (d / "2022_01").exists()
    assert (d / "2022_02").exists()

    assert all(f.exists() for f in targets if f.suffix == ".txt")


def test_takes_multiple_file_specs(tmp_path: Path):
    d = tmp_path / "files"
    print(f"tmp_path: {d}")
    d.mkdir()
    test_dt = datetime.fromisoformat("2022-02-14")
    files = make_test_files(d, test_dt)
    targets = [Path(d / mo_dir(f) / f.name) for f in files]

    os.chdir(d)
    assert str(Path.cwd()) == str(d)

    args = ["bymo.py", "-m", "*.txt", "*.opt"]
    bymo.main(args)

    # Should move only specified files when -m argument is also passed.
    assert all(f.exists() for f in files if f.suffix == ".ini")
    assert all(not f.exists() for f in files if f.suffix in ["*.opt", ".txt"])

    assert (d / "2021_12").exists()
    assert (d / "2022_01").exists()
    assert (d / "2022_02").exists()

    assert all(f.exists() for f in targets if f.suffix in ["*.opt", ".txt"])
