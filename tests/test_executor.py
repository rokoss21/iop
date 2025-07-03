import executor


def test_is_dangerous_detects_rm_rf_root():
    assert executor._is_dangerous("rm -rf /")


def test_is_dangerous_safe_command():
    assert not executor._is_dangerous("echo hello")