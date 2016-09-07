"""Unit tests for DanceCat.Models.Schedule model."""

from __future__ import print_function
import sys
import datetime
from DanceCat import db
from DanceCat import Models
from DanceCat import Constants
import pytest
import sqlalchemy.exc as sqlalchemy_exc


# Set fixed time at 2016-09-01 18:19:20.
FIXED_TIME = datetime.datetime(2016, 9, 1, 18, 19, 20)


@pytest.fixture
def patch_datetime_now(monkeypatch):
    """Patch datetime.now function to return fixed timestamp."""
    def set_time(manual_ret_time=FIXED_TIME):
        class FixedDateTime(datetime.datetime):
            """Mock datetime class."""
            @classmethod
            def now(cls):
                """Return chosen datetime."""
                return manual_ret_time

        monkeypatch.setattr(datetime, 'datetime', FixedDateTime)

    return set_time


@pytest.fixture
def setup_to_add_job(app, user_email):
    """Setup data so we can test Schedule Model."""
    allowed_email = Models.AllowedEmail(user_email)
    db.session.add(allowed_email)
    db.session.commit()

    user = Models.User(user_email, '123456')
    db.session.add(user)
    db.session.commit()

    connection = Models.Connection(
        Constants.DB_MYSQL,
        'localhost',
        'test_db',
        user.user_id,
        user_name='db_user'
    )
    db.session.add(connection)
    db.session.commit()

    job = Models.QueryDataJob(
        'test job',
        'select * from table_1',
        user.user_id
    )
    db.session.add(job)
    db.session.commit()


def some_datetime_func():
    """Mock datetime function to test patch_datetime_now fixture."""
    return datetime.datetime.now()


def test_ensure_fixed_datetime_work(patch_datetime_now):
    """Test the patch_datetime_now fixture."""
    patch_datetime_now()
    assert datetime.datetime.now() == FIXED_TIME
    new_datetime = datetime.datetime(2016, 9, 1, 19, 20, 21)
    patch_datetime_now(new_datetime)
    assert datetime.datetime.now() == new_datetime
    assert some_datetime_func() == new_datetime


class TestScheduleModel(object):
    """Unit test for Schedule model class."""

    start_time_beautiful = datetime.datetime(2016, 9, 1, 0, 0, 0, 0)
    start_time_ugly = datetime.datetime(2016, 9, 3, 13, 21, 43)

    active_schedule_skeleton = {
        'job_id': 1,
        'user_id': 1,
        'is_active': True
    }

    in_active_schedule_skeleton = {
        'job_id': 1,
        'user_id': 1,
        'is_active': False
    }

    def test_should_add_new_schedule(self,
                                     setup_to_add_job
                                     ):
        job = Models.QueryDataJob.query.get(1)
        assert job.job_id == 1

        hourly_schedule = Models.Schedule(
            schedule_type=Constants.SCHEDULE_HOURLY,
            start_time=self.start_time_beautiful,
            **self.active_schedule_skeleton
        )
        db.session.add(hourly_schedule)
        db.session.commit()
        datetime_now = datetime.datetime.now()
        datetime_delta_created_on = datetime_now - hourly_schedule.created_on
        datetime_delta_last_updated = \
            datetime_now - hourly_schedule.last_updated

        assert hourly_schedule.schedule_id == 1
        assert hourly_schedule._is_active
        assert not hourly_schedule.is_deleted
        assert hourly_schedule.is_active
        assert hourly_schedule.next_run > self.start_time_beautiful
        assert hourly_schedule.minute_of_hour == 0
        assert hourly_schedule.hour_of_day == 0
        # 0 for Monday -> 3 for Thursday
        assert hourly_schedule.day_of_week == 3
        assert hourly_schedule.day_of_month == 1
        assert hourly_schedule.schedule_type == Constants.SCHEDULE_HOURLY
        assert round(datetime_delta_created_on.total_seconds()) == 0
        assert round(datetime_delta_last_updated.total_seconds()) == 0
        assert hourly_schedule.version == Constants.MODEL_SCHEDULE_VERSION
        assert str(hourly_schedule) == \
            '<Schedule Id 1 of Job Id 1>'

        daily_schedule = Models.Schedule(
            schedule_type=Constants.SCHEDULE_DAILY,
            start_time=self.start_time_ugly,
            **self.in_active_schedule_skeleton
        )
        db.session.add(daily_schedule)
        db.session.commit()

        assert not daily_schedule._is_active
        assert not daily_schedule.is_active
        assert daily_schedule.next_run > self.start_time_ugly
        assert daily_schedule.minute_of_hour == 21
        assert daily_schedule.hour_of_day == 13
        # 0 for Monday -> 5 for Saturday
        assert daily_schedule.day_of_week == 5
        assert daily_schedule.day_of_month == 3
        assert daily_schedule.schedule_type == Constants.SCHEDULE_DAILY

        with pytest.raises(TypeError):
            invalid_schedule = Models.Schedule(
                **self.active_schedule_skeleton
            )

        # Since we don't update next run for one time schedule,
        # we expect passed start time in the future.
        with pytest.raises(ValueError):
            once_schedule = Models.Schedule(
                schedule_type=Constants.SCHEDULE_ONCE,
                start_time=self.start_time_ugly,
                **self.active_schedule_skeleton
            )

        with pytest.raises(AttributeError):
            monthly_of_void = Models.Schedule(
                schedule_type=Constants.SCHEDULE_MONTHLY,
                start_time=None,
                **self.in_active_schedule_skeleton
            )

        active_schedules = Models.Schedule.query.filter(
            Models.Schedule.is_active
        ).count()
        assert active_schedules == 1
