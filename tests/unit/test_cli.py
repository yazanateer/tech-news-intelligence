import pytest

from scripts.common import INTERRUPTED_EXIT_CODE, run_cli


def test_run_cli_exits_cleanly_on_keyboard_interrupt() -> None:
    def interrupted() -> None:
        raise KeyboardInterrupt

    with pytest.raises(SystemExit) as exit_info:
        run_cli(interrupted)

    assert exit_info.value.code == INTERRUPTED_EXIT_CODE


def test_run_cli_runs_main() -> None:
    calls = []

    run_cli(lambda: calls.append("ran"))

    assert calls == ["ran"]
