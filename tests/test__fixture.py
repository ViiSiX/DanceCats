"""This module contains test cases for the test's fixtures."""

import datetime
from dateutil.relativedelta import relativedelta


# Set fixed time at 2016-09-01 18:19:20.
FIXED_TIME = datetime.datetime(2016, 9, 1, 18, 19, 20)


def some_datetime_func():
    """Mock datetime function to test patch_datetime_now fixture."""
    return datetime.datetime.now() + relativedelta(minutes=2)


def test_ensure_fixed_datetime_work(freeze_datetime):
    """Test the patch_datetime_now fixture."""
    freeze_datetime.freeze(FIXED_TIME)
    assert datetime.datetime.now() == FIXED_TIME
    new_datetime = datetime.datetime(2016, 9, 1, 19, 20, 21)
    freeze_datetime.freeze(new_datetime)
    assert datetime.datetime.now() == new_datetime
    assert some_datetime_func() == datetime.datetime(2016, 9, 1, 19, 22, 21)
