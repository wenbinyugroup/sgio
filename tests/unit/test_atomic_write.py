"""Unit tests for `sgio.utils.io.atomic_write`.

A streaming writer fills its target incrementally, so a failure part way
through used to leave a truncated file behind -- and a plain ``open(..., 'w')``
destroys a previously valid file before the first byte is even written.
"""

from __future__ import annotations

import pytest

from sgio.utils.io import atomic_write


@pytest.mark.unit
def test_atomic_write_creates_the_file_on_success(tmp_path):
    """The target appears with the full content once the block completes."""
    target = tmp_path / "out.sc"

    with atomic_write(str(target)) as file:
        file.write("content\n")

    assert target.read_text() == "content\n"


@pytest.mark.unit
def test_atomic_write_leaves_no_file_on_failure(tmp_path):
    """A failure part way through must not leave a partial file."""
    target = tmp_path / "out.sc"

    with pytest.raises(RuntimeError):
        with atomic_write(str(target)) as file:
            file.write("half a file")
            raise RuntimeError("writer blew up")

    assert not target.exists()
    assert list(tmp_path.iterdir()) == []


@pytest.mark.unit
def test_atomic_write_keeps_the_previous_file_on_failure(tmp_path):
    """An existing valid file must survive a failed rewrite untouched."""
    target = tmp_path / "out.sc"
    target.write_text("previous good content\n")

    with pytest.raises(RuntimeError):
        with atomic_write(str(target)) as file:
            file.write("half a file")
            raise RuntimeError("writer blew up")

    assert target.read_text() == "previous good content\n"
