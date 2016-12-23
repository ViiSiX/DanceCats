"""
Docstring for DanceCat.FrequencyTaskChecker(FTC) module.

This module will be used to check the schedule and
enqueue the next running job into the queue.
"""

from __future__ import print_function
import time
import datetime
import atexit
import signal
from setproctitle import setproctitle
from dateutil.relativedelta import relativedelta as dateutil_relativedelta
from DanceCat import Helpers
from DanceCat import app, db, rdb
from DanceCat.Models import Schedule, TrackJobRun
from DanceCat.JobWorker import job_worker_query


class FrequencyTaskChecker(Helpers.Daemonize):
    """
    Frequency Task Checker class.

    This class will check and enqueue scheduled jobs
    when the running time will come. After that sleep
    for `interval` seconds and repeat.
    """

    PROCESS_TITLE = 'frequency task checker'
    PROCESS_TITLE_SHORT = 'FTC'

    def __init__(self, pid_path='frequency.pid', interval=60):
        """
        Constructor for FrequencyTaskChecker class.

        :param interval: Seconds the checker will sleep throughout idle time.
        :type interval: int
        """
        Helpers.Daemonize.__init__(self, pid_path)
        self.interval = interval

    def run(self):
        """
        This method will check and enqueue scheduled jobs
        when the running time will come. After that sleep
        for `interval` seconds and repeat.
        """
        atexit.register(self._exit_handler)
        signal.signal(signal.SIGINT, self._exit_handler)
        signal.signal(signal.SIGTERM, self._exit_handler)
        setproctitle(self.PROCESS_TITLE_SHORT + ' ' + self.pid_path)

        while True:
            try:
                self.task_checker()
                Helpers.fq_sleep(
                    self.interval - Helpers.Timer().get_total_seconds()
                )
            except Exception as e:
                print('[{0}] {1}'.format(self.PROCESS_TITLE, e))
                self._remove_zombie_process()
                break
        self._exit_handler()

    def task_checker(self):
        """
        This method will check and enqueue scheduled jobs for run method.
        """
        cur_time = datetime.datetime.now()
        if cur_time.second < 2:
            time.sleep(2 - cur_time.second)
        print(
            "[FQ] Checking and scheduling at {start_time}".
            format(start_time=cur_time)
        )

        next_schedules = Schedule.query.filter(
            Schedule.is_active,
            Schedule.next_run >= cur_time,
            Schedule.next_run < cur_time + dateutil_relativedelta(
                seconds=self.interval
            )
        ).all()

        with app.app_context():
            for next_schedule in next_schedules:
                if next_schedule.Job.is_active:
                    tracker = TrackJobRun(job_id=next_schedule.Job.job_id,
                                          schedule_id=next_schedule.schedule_id
                                          )
                    db.session.add(tracker)
                    db.session.commit()

                    queue = rdb.queue['default']
                    queue.enqueue(
                        f=job_worker_query, kwargs={
                            'job_id': next_schedule.Job.job_id,
                            'tracker_id': tracker.track_job_run_id
                        },
                        timeout=app.config.get(
                            'JOB_WORKER_EXECUTE_TIMEOUT', 3600
                        ),
                        ttl=app.config.get(
                            'JOB_WORKER_ENQUEUE_TIMEOUT', 1800
                        ),
                        result_ttl=app.config.get(
                            'JOB_RESULT_VALID_SECONDS', 86400
                        ),
                        job_id="{tracker_id}".format(
                            tracker_id=tracker.track_job_run_id
                        )
                    )

                next_schedule.update_next_run(
                    validated=True,
                    interval=self.interval)
                db.session.commit()
