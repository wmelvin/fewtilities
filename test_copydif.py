import os
import pytest
import shutil

from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

import copydif


base_dt = datetime(2023, 1, 16, 13, 33, 0)


def set_mtime_per_base(file_name: str, minutes: int):
    if minutes:
        file_dt = base_dt + timedelta(minutes=minutes)
    else:
        file_dt = base_dt
    new_ts = file_dt.timestamp()
    os.utime(file_name, (new_ts, new_ts))


@pytest.fixture
def source_3files_and_target(tmp_path) -> Tuple[Path, Path]:
    root_path: Path = tmp_path
    source_path = root_path / "source"
    source_path.mkdir()
    target_path = root_path / "target"
    target_path.mkdir()
    f1 = source_path / "file1.txt"
    f2 = source_path / "file2.csv"
    f3 = source_path / "file3.dat"
    f1.write_text("file1")
    f2.write_text("file2")
    f3.write_text("file3")
    set_mtime_per_base(str(f1), 0)
    set_mtime_per_base(str(f2), 0)
    set_mtime_per_base(str(f3), 0)
    return source_path, target_path


def test_help(capsys):
    args = ["copydif.py", "-h"]

    with pytest.raises(SystemExit):
        copydif.main(args)

    captured = capsys.readouterr()

    assert "[-h]" in captured.out
    assert "copydif.py (v." in captured.out


def test_copies_to_empty_target(source_3files_and_target):
    source_path, target_path = source_3files_and_target

    assert len(list(target_path.glob("*"))) == 0

    args = ["copydif.py", str(source_path), str(target_path)]
    result = copydif.main(args)

    assert result == 0
    assert len(list(target_path.glob("*"))) == 3


def test_copies_file_per_wildcard(source_3files_and_target):
    source_path, target_path = source_3files_and_target

    assert len(list(target_path.glob("*"))) == 0

    src_spec = str(source_path.joinpath("*.txt"))

    args = ["copydif.py", src_spec, str(target_path)]
    result = copydif.main(args)

    assert result == 0
    assert len(list(target_path.glob("*"))) == 1


def test_copies_files_per_wildcard(source_3files_and_target):
    source_path, target_path = source_3files_and_target

    assert len(list(target_path.glob("*"))) == 0

    src_spec = str(source_path.joinpath("*"))

    args = ["copydif.py", src_spec, str(target_path)]
    result = copydif.main(args)

    assert result == 0
    assert len(list(target_path.glob("*"))) == 3


def test_detects_files_same(source_3files_and_target, capsys):
    source_path, target_path = source_3files_and_target

    for file in list(source_path.glob("*")):
        shutil.copy2(file, target_path.joinpath(file.name))

    assert len(list(target_path.glob("*"))) == 3

    args = ["copydif.py", str(source_path), str(target_path)]
    result = copydif.main(args)

    captured = capsys.readouterr()

    assert result == 0
    # assert "Same:" in captured.out
    # assert "COPY:" not in captured.out
    assert captured.out.count("Same:") == 3
    assert captured.out.count("COPY:") == 0


def test_detects_file_mtime(source_3files_and_target, capsys):
    source_path, target_path = source_3files_and_target

    src_files = sorted(source_path.glob("*"))

    for file in src_files:
        shutil.copy2(file, target_path.joinpath(file.name))

    set_mtime_per_base(src_files[0], minutes=-1)

    set_mtime_per_base(src_files[2], minutes=1)

    assert len(list(target_path.glob("*"))) == 3

    args = ["copydif.py", str(source_path), str(target_path)]
    result = copydif.main(args)

    captured = capsys.readouterr()

    assert result == 0
    assert captured.out.count("Same:") == 1
    assert captured.out.count("COPY:") == 2


def test_detects_file_size(source_3files_and_target, capsys):
    source_path, target_path = source_3files_and_target

    src_files = sorted(source_path.glob("*"))

    for file in src_files:
        shutil.copy2(file, target_path.joinpath(file.name))

    Path(src_files[0]).write_text(
        "Not sure why my size is different but my mtime is the same."
    )

    set_mtime_per_base(src_files[0], minutes=0)

    assert len(list(target_path.glob("*"))) == 3

    args = ["copydif.py", str(source_path), str(target_path)]
    result = copydif.main(args)

    captured = capsys.readouterr()

    assert result == 0
    assert captured.out.count("Same:") == 2
    assert captured.out.count("COPY:") == 1


def test_missing_source(source_3files_and_target, capsys):
    source_path, target_path = source_3files_and_target
    source_path = source_path.joinpath("ImNotHere")  # No mkdir.

    args = ["copydif.py", str(source_path), str(target_path)]
    result = copydif.main(args)

    captured = capsys.readouterr()

    assert result == 0
    assert "No files found matching" in captured.out


def test_log_file(source_3files_and_target):
    source_path, target_path = source_3files_and_target

    log_path = target_path / "copydif.log"
    print(log_path)

    assert len(list(target_path.glob("*"))) == 0

    args = [
        "copydif.py",
        str(source_path),
        str(target_path),
        f"--log-file={log_path}",
    ]
    result = copydif.main(args)

    assert result == 0
    assert len(list(target_path.glob("*"))) == 4
    assert log_path.exists()


def test_bad_log_file(source_3files_and_target, capsys):
    source_path, target_path = source_3files_and_target

    log_path = str(target_path)  # Is a directory.
    print(log_path)

    args = [
        "copydif.py",
        str(source_path),
        str(target_path),
        f"--log-file={log_path}",
    ]
    with pytest.raises(SystemExit):
        copydif.main(args)

    captured = capsys.readouterr()

    assert "not a file" in captured.err


def test_bad_target_path(source_3files_and_target, capsys):
    source_path, target_path = source_3files_and_target
    bad_target = target_path.joinpath("ImNotHere")  # No mkdir.

    args = [
        "copydif.py",
        str(source_path),
        str(bad_target),
    ]
    with pytest.raises(SystemExit):
        copydif.main(args)

    captured = capsys.readouterr()

    assert "Cannot find target" in captured.err


def test_no_args(capsys):
    args = ["copydif.py"]  # Well there is arg[0].
    with pytest.raises(SystemExit):
        copydif.main(args)
    captured = capsys.readouterr()
    assert "arguments are required" in captured.err


def test_no_target_path(tmp_path, capsys):
    source_path = tmp_path
    args = [
        "copydif.py",
        str(source_path),
    ]
    with pytest.raises(SystemExit):
        copydif.main(args)
    captured = capsys.readouterr()
    assert "arguments are required" in captured.err


def test_copies_files_per_list_file(source_3files_and_target):
    source_path, target_path = source_3files_and_target

    src_files = sorted(source_path.glob("*"))

    assert len(src_files) == 3

    #  Put the path to the first and third file into the list file.
    lines = f"{src_files[0]}\n{src_files[2]}\n"
    list_file: Path = source_path.parent / "listfile.txt"
    list_file.write_text(lines)

    assert len(list(target_path.glob("*"))) == 0

    args = ["copydif.py", f"@{list_file}", str(target_path)]
    result = copydif.main(args)

    assert result == 0
    assert len(list(target_path.glob("*"))) == 2


def test_source_only_has_dir(source_3files_and_target, capsys):
    source_path, target_path = source_3files_and_target

    #  Parent of source_path only has the original source_path dir.
    source_path = source_path.parent

    args = ["copydif.py", str(source_path), str(target_path)]
    result = copydif.main(args)

    captured = capsys.readouterr()

    assert result == 0
    assert "No files found matching" in captured.out
