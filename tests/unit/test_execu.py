"""Unit tests for solver success detection in ``sgio.utils.execu.run``."""
from __future__ import annotations

import subprocess as sbp

import pytest

import sgio.utils.execu as sue
from sgio._exceptions import (
    SwiftCompError,
    SwiftCompIOError,
    SwiftCompLicenseError,
    VABSError,
)

SC_FULL_PATH = r'C:\Program Files\AnalySwift\SwiftComp.exe'
VABS_FULL_PATH = r'C:\Program Files\AnalySwift\VABS.exe'


def _fake_solver(monkeypatch, resolved: str, stdout: str) -> list:
    """Make ``which`` return ``resolved`` and ``subprocess.run`` print ``stdout``."""
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return sbp.CompletedProcess(cmd, 0, stdout=stdout, stderr='')

    monkeypatch.setattr(sue.shutil, 'which', lambda name: resolved)
    monkeypatch.setattr(sue.sbp, 'run', fake_run)
    return calls


@pytest.mark.unit
class TestSolverOutputCheckWithResolvedPath:
    """``which`` resolves the solver to a full path, as on a real install."""

    def test_swiftcomp_failure_raises(self, monkeypatch):
        _fake_solver(
            monkeypatch, SC_FULL_PATH,
            'Reading input...\n determinant of Jacobian matrix less than 0 \n',
        )

        with pytest.raises(SwiftCompError, match='Jacobian'):
            sue.run(['SwiftComp', 'bad.sc', '1D', 'H'], timeout=10)

    def test_swiftcomp_success_returns(self, monkeypatch):
        calls = _fake_solver(
            monkeypatch, SC_FULL_PATH,
            'SwiftComp finished successfully\nTotal time 0.1 s\n',
        )

        out = sue.run(['SwiftComp', 'good.sc', '1D', 'H'], timeout=10)

        assert out.returncode == 0
        assert calls[0][0] == SC_FULL_PATH

    def test_empty_output_raises(self, monkeypatch):
        _fake_solver(monkeypatch, SC_FULL_PATH, '')

        with pytest.raises(SwiftCompError, match='No output'):
            sue.run(['SwiftComp', 'bad.sc', '1D', 'H'], timeout=10)

    def test_license_error(self, monkeypatch):
        _fake_solver(monkeypatch, SC_FULL_PATH, 'Checking license failed\n')

        with pytest.raises(SwiftCompLicenseError):
            sue.run(['SwiftComp', 'a.sc', '3D', 'H'], timeout=10)

    def test_io_error(self, monkeypatch):
        _fake_solver(monkeypatch, SC_FULL_PATH, 'I/O error reading a.sc\n')

        with pytest.raises(SwiftCompIOError):
            sue.run(['SwiftComp', 'a.sc', '3D', 'H'], timeout=10)

    def test_vabs_failure_raises(self, monkeypatch):
        _fake_solver(monkeypatch, VABS_FULL_PATH, 'Something went wrong\n')

        with pytest.raises(VABSError):
            sue.run(['VABS', 'bad.sg'], timeout=10)

    def test_vabs_success_returns(self, monkeypatch):
        _fake_solver(
            monkeypatch, VABS_FULL_PATH,
            'VABS finished successfully\nTotal time 0.1 s\n',
        )

        assert sue.run(['VABS', 'good.sg'], timeout=10).returncode == 0

    def test_full_path_command_is_recognized(self, monkeypatch):
        _fake_solver(monkeypatch, SC_FULL_PATH, 'failed\n')

        with pytest.raises(SwiftCompError):
            sue.run([SC_FULL_PATH, 'bad.sc', '3D', 'H'], timeout=10)

    def test_batch_wrapper_is_recognized(self, monkeypatch):
        _fake_solver(monkeypatch, r'C:\Windows\System32\cmd.exe', 'failed\n')

        with pytest.raises(SwiftCompError):
            sue.run(['swiftcomp.bat', 'bad.sc', '3D', 'H'], timeout=10)

    def test_non_solver_command_is_not_checked(self, monkeypatch):
        _fake_solver(monkeypatch, r'C:\tools\gmsh.exe', '')

        assert sue.run(['gmsh', 'a.geo'], timeout=10).returncode == 0
