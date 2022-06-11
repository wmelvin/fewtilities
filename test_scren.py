from pathlib import Path
from typing import List

import os

import scren


def test_scren(tmp_path: Path):
    d = tmp_path / "Pictures"
    d.mkdir()

    files: List[Path] = []

    #  Pattern 1:
    files.append(d / "Screenshot_from_2022-02-03_17-31-01.png")
    files.append(d / "Screenshot from 2022-02-24 14-20-02.png")
    files.append(d / "Screenshot_from_2022-02-22_07-59-03-crop.jpg")
    files.append(d / "Screenshot at 2022-02-12 09-10-04.png")
    files.append(d / "Screenshot_2022-03-01_07-08-05.png")

    #  Pattern 2:
    files.append(d / "Screenshot_20220301_070806.png")

    for f in files:
        f.write_bytes(b"0")
        assert f.exists()

    os.chdir(d)
    assert str(Path.cwd()) == str(d)

    args = ["scren.py"]
    scren.main(args)

    # Should not move files when -m argument is not passed.
    assert all(f.exists() for f in files)

    args = ["scren.py", "-m"]
    scren.main(args)

    # Should move (rename) files when -m argument is passed.
    assert all(not f.exists() for f in files)

    assert len(list(d.glob("screen_*"))) == len(files)
