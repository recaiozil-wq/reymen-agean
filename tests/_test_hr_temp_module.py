# Temporary module for hot_reload test - created by test_hot_reload.py
# Contains motor_kaydet function for testing _reload_modul

TEST_VAR = "initial_value"


def motor_kaydet(motor):
    """Test motor_kaydet function."""
    motor._test_called = True
