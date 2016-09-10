"""Unit tests for DanceCat.Models.Schedule model."""

from __future__ import print_function
import datetime
from dateutil.relativedelta import relativedelta
from DanceCat import db
from DanceCat import Models
from DanceCat import Constants
import pytest


class TestScheduleModel(object):
    """Unit test for Schedule model class."""

    start_time_beautifully = datetime.datetime(2016, 9, 1, 0, 0, 0, 0)
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

    def test_should_add_new_schedules(self,
                                      setup_to_add_job
                                      ):
        """Test if schedules should be added and should be active."""
        job = Models.QueryDataJob.query.get(1)
        assert job.job_id == 1

        hourly_schedule = Models.Schedule(
            schedule_type=Constants.SCHEDULE_HOURLY,
            start_time=self.start_time_beautifully,
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
        assert hourly_schedule.next_run > self.start_time_beautifully
        assert hourly_schedule.minute_of_hour == 0
        assert hourly_schedule.hour_of_day == 0
        # Weekday: 0 for Monday -> 6 for Sunday
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
        # Weekday: 0 for Monday -> 6 for Sunday
        assert daily_schedule.day_of_week == 5
        assert daily_schedule.day_of_month == 3
        assert daily_schedule.schedule_type == Constants.SCHEDULE_DAILY

        assert Models.Schedule.query.count() == 2

    def test_would_schedule_active(self, setup_to_add_job):
        """Test if schedules remain active setting it _is_active values."""
        schedule_1 = Models.Schedule(
            schedule_type=Constants.SCHEDULE_HOURLY,
            start_time=self.start_time_beautifully,
            **self.active_schedule_skeleton
        )
        db.session.add(schedule_1)
        db.session.commit()

        schedule_2 = Models.Schedule(
            schedule_type=Constants.SCHEDULE_MONTHLY,
            start_time=self.start_time_ugly,
            **self.active_schedule_skeleton
        )
        db.session.add(schedule_2)
        db.session.commit()

        schedule_3 = Models.Schedule(
            schedule_type=Constants.SCHEDULE_WEEKLY,
            start_time=self.start_time_ugly,
            **self.in_active_schedule_skeleton
        )
        db.session.add(schedule_3)
        db.session.commit()

        assert Models.Schedule.query.count() == 3
        assert Models.Schedule.query.filter(
            Models.Schedule.is_active
        ).count() == 2

        schedule_2.is_active = False
        assert Models.Schedule.query.filter(
            Models.Schedule.is_active
        ).count() == 1

    def test_would_schedule_init_raise_missing(self, setup_to_add_job):
        """Test if schedule initialization raise error when missing args."""
        with pytest.raises(TypeError):
            schedule = Models.Schedule(
                **self.active_schedule_skeleton
            )

        with pytest.raises(TypeError):
            schedule = Models.Schedule(
                schedule_type=Constants.SCHEDULE_MONTHLY,
                start_time=None,
                **self.in_active_schedule_skeleton
            )

    def test_would_schedule_init_raise_value_error(self, setup_to_add_job):
        """For Once type schedule, expect the start time is in the future."""
        with pytest.raises(ValueError):
            schedule = Models.Schedule(
                schedule_type=Constants.SCHEDULE_ONCE,
                start_time=self.start_time_ugly,
                **self.active_schedule_skeleton
            )

    def test_would_delete_schedule(self,
                                   setup_to_add_job
                                   ):
        """Test if a schedule will be logically deleted."""
        schedule = Models.Schedule(
            schedule_type=Constants.SCHEDULE_HOURLY,
            start_time=self.start_time_beautifully,
            **self.active_schedule_skeleton
        )
        db.session.add(schedule)
        db.session.commit()

        no_active_schedules = Models.Schedule.query.filter(
            Models.Schedule.is_active
        ).count()
        assert no_active_schedules == 1

        schedule.is_deleted = True
        db.session.commit()
        assert schedule.is_deleted
        assert schedule._is_active
        assert not schedule.is_active

        no_active_schedules = Models.Schedule.query.filter(
            Models.Schedule.is_active
        ).count()
        assert no_active_schedules == 0

        no_schedules = Models.Schedule.query.count()
        assert no_schedules == 1

    def test_would_once_schedule_validate_value_on_update(
            self, setup_to_add_job
    ):
        """Check if the Once schedule is valid or not."""
        schedule = Models.Schedule(
            schedule_type=Constants.SCHEDULE_HOURLY,
            start_time=self.start_time_beautifully,
            **self.active_schedule_skeleton
        )

        # Once upon a time
        schedule.schedule_type = Constants.SCHEDULE_ONCE
        with pytest.raises(ValueError):
            schedule.update_start_time(self.start_time_ugly)

    def test_would_hourly_schedule_validate_work(self, setup_to_add_job):
        """Check if Schedule.validate is working for Hourly type or not."""
        schedule = Models.Schedule(
            schedule_type=Constants.SCHEDULE_HOURLY,
            start_time=self.start_time_beautifully,
            **self.active_schedule_skeleton
        )

        # Hourly
        for minute_of_hour in [-1, 60, 61]:
            schedule.minute_of_hour = minute_of_hour
            assert not schedule.validate()
        for minute_of_hour in [0, 4, 59]:
            schedule.minute_of_hour = minute_of_hour
            assert schedule.validate()
        # Do not care about others
        schedule.hour_of_day = 99
        schedule.day_of_week = 9
        schedule.day_of_month = -4
        assert schedule.validate()

    def test_would_daily_schedule_validate_work(self, setup_to_add_job):
        """Check if Schedule.validate is working for Daily type or not."""
        schedule = Models.Schedule(
            schedule_type=Constants.SCHEDULE_DAILY,
            start_time=self.start_time_beautifully,
            **self.active_schedule_skeleton
        )

        # Daily
        for minute_of_hour, hour_of_day in [
                # Both wrong
                (-1, -1),
                (60, 25),
                # One wrong
                (1, -1),
                (2, 24)
        ]:
            schedule.minute_of_hour = minute_of_hour
            schedule.hour_of_day = hour_of_day
            assert not schedule.validate()
        for minute_of_hour, hour_of_day in [
                (0, 10),
                (19, 23)
        ]:
            schedule.minute_of_hour = minute_of_hour
            schedule.hour_of_day = hour_of_day
            assert schedule.validate()
        # Do not care about others
        schedule.day_of_week = 300
        schedule.day_of_month = 8
        assert schedule.validate()

    def test_would_weekly_schedule_validate_work(self, setup_to_add_job):
        """Check if Schedule.validate is working for Weekly type or not."""
        schedule = Models.Schedule(
            schedule_type=Constants.SCHEDULE_WEEKLY,
            start_time=self.start_time_beautifully,
            **self.active_schedule_skeleton
        )

        # Day of Week: 0 for Mon -> 6 for Sun
        for minute_of_hour, hour_of_day, day_of_week in [
                (-1, 0, 2),
                (2, 55, 3),
                (3, 14, 7)
        ]:
            schedule.minute_of_hour = minute_of_hour
            schedule.hour_of_day = hour_of_day
            schedule.day_of_week = day_of_week
            assert not schedule.validate()
        for minute_of_hour, hour_of_day, day_of_week in [
                (1, 1, 1),
                (59, 23, 6)
        ]:
            schedule.minute_of_hour = minute_of_hour
            schedule.hour_of_day = hour_of_day
            schedule.day_of_week = day_of_week
            assert schedule.validate()
        # Do not care about others
        schedule.day_of_month = 999
        assert schedule.validate()

    def test_would_monthly_schedule_validate_work(self, setup_to_add_job):
        """Check if Schedule.validate is working for Monthly type or not."""
        schedule = Models.Schedule(
            schedule_type=Constants.SCHEDULE_MONTHLY,
            start_time=self.start_time_beautifully,
            **self.active_schedule_skeleton
        )

        # Monthly
        for minute_of_hour, hour_of_day, day_of_month in [
            (-1, 0, 2),
            (2, 55, 3),
            (3, 14, -1),
            (3, 14, 44)
        ]:
            schedule.minute_of_hour = minute_of_hour
            schedule.hour_of_day = hour_of_day
            schedule.day_of_month = day_of_month
            assert not schedule.validate()
        for minute_of_hour, hour_of_day, day_of_month in [
            (1, 1, 26),
            (59, 23, 29)
        ]:
            schedule.minute_of_hour = minute_of_hour
            schedule.hour_of_day = hour_of_day
            schedule.day_of_month = day_of_month
            assert schedule.validate()
        # Do not care about others
        schedule.day_of_week = 33
        assert schedule.validate()

    def test_would_add_once_schedule_with_current_time(
            self,
            setup_to_add_job
    ):
        with pytest.raises(ValueError):
            Models.Schedule(
                schedule_type=Constants.SCHEDULE_ONCE,
                start_time=datetime.datetime.now(),
                **self.active_schedule_skeleton
            )

    def test_would_schedule_once_update_next_run(
            self, setup_to_add_job, freeze_datetime
    ):
        """Test Models.Schedule.update_next_run of Once Schedule type.

        The ugly timestamp is in the future of beautiful timestamp.
        Plus Once Schedule type run only once at ugly timestamp,
        therefore no update for this Schedule type.
        """
        freeze_datetime.freeze(self.start_time_beautifully)
        schedule = Models.Schedule(
            schedule_type=Constants.SCHEDULE_ONCE,
            start_time=self.start_time_ugly,
            **self.active_schedule_skeleton
        )

        schedule.update_next_run()
        assert schedule.next_run == self.start_time_ugly

    def test_would_schedule_hourly_update_next_run(
            self, setup_to_add_job, freeze_datetime
    ):
        """Test Models.Schedule.update_next_run of Hourly Schedule type."""
        freeze_datetime.freeze(self.start_time_beautifully)
        schedule = Models.Schedule(
            schedule_type=Constants.SCHEDULE_HOURLY,
            start_time=self.start_time_ugly,
            **self.active_schedule_skeleton
        )

        # Update at beautiful timestamp, yet the start time in
        # the future, therefore no change.
        schedule.update_next_run()
        assert schedule.next_run == self.start_time_ugly

        # Start timestamp at beautiful timestamp.
        expected_next_run = datetime.datetime(2016, 9, 1, 1, 0, 0)
        schedule.update_start_time(self.start_time_beautifully)
        assert schedule.next_run == expected_next_run
        # For following cases, expect next run time would be
        # 2016-09-01 01:00:00.
        # Before update, next run time already at
        # 2016-09-01 01:00:00.
        # FrequencyTaskChecker interval is 60 seconds.
        #   The schedule is Hourly at minute of zero.
        #   2016-08-31 23:51:57 -> the result of update function will be
        #       2016-09-00 00:00:00 lesser than 2016-09-01 01:00:00,
        #       therefore remain at 2016-09-01 01:00:00.
        #   2016-08-31 23:59:57 -> next check time will be
        #       2016-09-00 00:00:57, result of update function is
        #       2016-09-00 00:01:57 -> convert second to zero.
        #   2016-09-01 00:00:01 -> 2016-09-01 01:00:01 -> 2016-09-01 01:00:00.
        #   2016-09-01 00:02:23 -> same as above.
        #   2016-09-01 00:51:53 -> 2016-09-01 01:00:53 -> 2016-09-01 01:00:00
        #   2016-09-01 00:58:54 -> 2016-09-01 01:00:54 -> 2016-09-01 01:00:00
        for cur_time in [
                datetime.datetime(2016, 8, 31, 23, 51, 57),
                datetime.datetime(2016, 8, 31, 23, 59, 57),
                datetime.datetime(2016, 9, 1, 0, 0, 1),
                datetime.datetime(2016, 9, 1, 0, 2, 23),
                datetime.datetime(2016, 9, 1, 0, 51, 53),
                datetime.datetime(2016, 9, 1, 0, 58, 54),
        ]:
            freeze_datetime.freeze(cur_time)
            schedule.update_next_run(interval=60)
            assert schedule.next_run == expected_next_run
        # For following cases, expect next run time would be
        # 2016-09-01 02:00:00.
        # Before update, next run time still at 2016-09-01 01:00:00.
        # FrequencyTaskChecker's interval will be 2 minutes.
        expected_next_run = datetime.datetime(2016, 9, 1, 2, 0, 0)
        for cur_time in [
                datetime.datetime(2016, 9, 1, 0, 58, 11),
                datetime.datetime(2016, 9, 1, 1, 0, 0),
                datetime.datetime(2016, 9, 1, 1, 1, 22),
        ]:
            freeze_datetime.freeze(cur_time)
            schedule.update_next_run(interval=120)
            assert schedule.next_run == expected_next_run

        # Start timestamp is ugly... really?
        freeze_datetime.freeze(self.start_time_beautifully)
        schedule.update_start_time(self.start_time_ugly)
        assert schedule.next_run == self.start_time_ugly
        schedule.update_next_run(interval=60)
        assert schedule.next_run == self.start_time_ugly
        freeze_datetime.freeze(datetime.datetime(2016, 9, 3, 13, 21, 11))
        schedule.update_next_run(interval=29)
        assert schedule.next_run == self.start_time_ugly
        # For following cases, expect next run time would be
        # 2016-09-03 14:21:00.
        # FrequencyTaskChecker's interval will be 29 seconds.
        expected_next_run = datetime.datetime(2016, 9, 3, 14, 21, 00)
        for cur_time in [
            self.start_time_ugly,
            datetime.datetime(2016, 9, 3, 13, 21, 33),
            datetime.datetime(2016, 9, 3, 13, 22, 00),
            datetime.datetime(2016, 9, 3, 13, 22, 34),
        ]:
            freeze_datetime.freeze(self.start_time_beautifully)
            schedule.update_start_time(self.start_time_ugly)
            freeze_datetime.freeze(cur_time)
            schedule.update_next_run(interval=29)
            assert schedule.next_run == expected_next_run

    def test_would_schedule_daily_update_next_run(
            self, setup_to_add_job, freeze_datetime
    ):
        """Test Models.Schedule.update_next_run of Daily Schedule type."""
        freeze_datetime.freeze(self.start_time_beautifully)
        schedule = Models.Schedule(
            schedule_type=Constants.SCHEDULE_DAILY,
            start_time=self.start_time_ugly,
            **self.active_schedule_skeleton
        )

        # Update at beautiful timestamp, yet the start time in
        # the future, therefore no change.
        schedule.update_next_run()
        assert schedule.next_run == self.start_time_ugly

        # Start timestamp at beautiful timestamp.
        expected_next_run = datetime.datetime(2016, 9, 2, 0, 0, 0)
        schedule.update_start_time(self.start_time_beautifully)
        assert schedule.next_run == expected_next_run
        for cur_time in [
            datetime.datetime(2016, 8, 31, 23, 59, 57),
            datetime.datetime(2016, 9, 1, 0, 0, 1),
            datetime.datetime(2016, 9, 1, 16, 51, 53),
            datetime.datetime(2016, 9, 1, 23, 59, 49),
        ]:
            freeze_datetime.freeze(
                self.start_time_beautifully - relativedelta(minutes=23)
            )
            schedule.update_start_time(self.start_time_beautifully)
            freeze_datetime.freeze(cur_time)
            schedule.update_next_run(interval=10)
            assert schedule.next_run == expected_next_run
        freeze_datetime.freeze(datetime.datetime(2016, 9, 4, 23, 59, 13))
        schedule.update_next_run(interval=30)
        assert schedule.next_run == datetime.datetime(2016, 9, 5, 0, 0, 0)

        # Start timestamp is ugly.
        expected_next_run = datetime.datetime(2016, 9, 4, 13, 21, 00)
        freeze_datetime.freeze(self.start_time_beautifully)
        schedule.update_start_time(self.start_time_ugly)
        assert schedule.next_run == self.start_time_ugly
        for cur_time in [
            self.start_time_ugly,
            datetime.datetime(2016, 9, 3, 19, 3, 4),
            datetime.datetime(2016, 9, 4, 5, 2, 22)
        ]:
            freeze_datetime.freeze(self.start_time_beautifully)
            schedule.update_start_time(self.start_time_ugly)
            freeze_datetime.freeze(cur_time)
            schedule.update_next_run(interval=60)
            assert schedule.next_run == expected_next_run

    def test_would_schedule_weekly_update_next_run(
            self, setup_to_add_job, freeze_datetime
    ):
        """Test Models.Schedule.update_next_run of Weekly Schedule type."""
        freeze_datetime.freeze(self.start_time_beautifully)
        schedule = Models.Schedule(
            schedule_type=Constants.SCHEDULE_WEEKLY,
            start_time=self.start_time_ugly,
            **self.active_schedule_skeleton
        )

        # Update at beautiful timestamp, yet the start time in
        # the future, therefore no change.
        schedule.update_next_run()
        assert schedule.next_run == self.start_time_ugly

        # Start timestamp at beautiful timestamp.
        # 2016-09-01 is Thursday, weekday will be 3.
        # We will focus on the next two Thursday:
        # 2016-09-08 and 2016-09-15.
        expected_next_run = datetime.datetime(2016, 9, 8, 0, 0, 0)
        schedule.update_start_time(self.start_time_beautifully)
        assert schedule.next_run == expected_next_run
        for cur_time in [
            datetime.datetime(2016, 8, 31, 23, 59, 57),
            datetime.datetime(2016, 9, 1, 0, 0, 1),
            datetime.datetime(2016, 9, 5, 16, 51, 53),
            datetime.datetime(2016, 9, 7, 23, 59, 49),
        ]:
            freeze_datetime.freeze(
                self.start_time_beautifully - relativedelta(minutes=3)
            )
            schedule.update_start_time(self.start_time_beautifully)
            freeze_datetime.freeze(cur_time)
            schedule.update_next_run(interval=10)
            assert schedule.next_run == expected_next_run
        freeze_datetime.freeze(datetime.datetime(2016, 9, 9, 23, 59, 13))
        schedule.update_next_run(interval=30)
        assert schedule.next_run == datetime.datetime(2016, 9, 15, 0, 0, 0)

        # Start timestamp is ugly.
        # 2016-09-03 is Saturday, weekday will be 5.
        # Focus on 2016-09-10.
        expected_next_run = datetime.datetime(2016, 9, 10, 13, 21, 00)
        freeze_datetime.freeze(self.start_time_beautifully)
        schedule.update_start_time(self.start_time_ugly)
        assert schedule.next_run == self.start_time_ugly
        for cur_time in [
            self.start_time_ugly,
            datetime.datetime(2016, 9, 8, 19, 3, 4),
            datetime.datetime(2016, 9, 10, 5, 2, 22)
        ]:
            freeze_datetime.freeze(self.start_time_beautifully)
            schedule.update_start_time(self.start_time_ugly)
            freeze_datetime.freeze(cur_time)
            schedule.update_next_run(interval=60)
            assert schedule.next_run == expected_next_run

    def test_would_schedule_monthly_update_next_run(
            self, setup_to_add_job, freeze_datetime
    ):
        """Test Models.Schedule.update_next_run of Monthly Schedule type."""
        freeze_datetime.freeze(self.start_time_beautifully)
        schedule = Models.Schedule(
            schedule_type=Constants.SCHEDULE_MONTHLY,
            start_time=self.start_time_ugly,
            **self.active_schedule_skeleton
        )

        # Update at beautiful timestamp, yet the start time in
        # the future, therefore no change.
        schedule.update_next_run()
        assert schedule.next_run == self.start_time_ugly

        # Start timestamp at beautiful timestamp.
        expected_next_run = datetime.datetime(2016, 10, 1, 0, 0, 0)
        schedule.update_start_time(self.start_time_beautifully)
        assert schedule.next_run == expected_next_run
        for cur_time in [
            datetime.datetime(2016, 8, 31, 23, 59, 57),
            datetime.datetime(2016, 9, 1, 0, 0, 1),
            datetime.datetime(2016, 9, 23, 16, 51, 53),
            datetime.datetime(2016, 9, 30, 23, 59, 49),
        ]:
            freeze_datetime.freeze(
                self.start_time_beautifully - relativedelta(minutes=3)
            )
            schedule.update_start_time(self.start_time_beautifully)
            freeze_datetime.freeze(cur_time)
            schedule.update_next_run(interval=10)
            assert schedule.next_run == expected_next_run
        freeze_datetime.freeze(datetime.datetime(2016, 9, 30, 23, 59, 33))
        schedule.update_next_run(interval=30)
        assert schedule.next_run == datetime.datetime(2016, 11, 1, 0, 0, 0)

        # Start timestamp is ugly.
        # 2016-09-03 is Saturday, weekday will be 5.
        # Focus on 2016-09-10.
        expected_next_run = datetime.datetime(2016, 10, 3, 13, 21, 00)
        freeze_datetime.freeze(self.start_time_beautifully)
        schedule.update_start_time(self.start_time_ugly)
        assert schedule.next_run == self.start_time_ugly
        for cur_time in [
            self.start_time_ugly,
            datetime.datetime(2016, 9, 8, 19, 3, 4),
            datetime.datetime(2016, 10, 1, 5, 2, 22)
        ]:
            freeze_datetime.freeze(self.start_time_beautifully)
            schedule.update_start_time(self.start_time_ugly)
            freeze_datetime.freeze(cur_time)
            schedule.update_next_run(interval=60)
            assert schedule.next_run == expected_next_run
