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
import sys
from dateutil.relativedelta import relativedelta
from multiprocessing import Process
from os import remove
from . import Helpers


def fq_sleep(sleep_time):
    """Print and sleep for <sleep_time> seconds."""
    print("[FQ] Sleeping for {seconds} second(s).".format(seconds=sleep_time))
    time.sleep(sleep_time)


def frequency_checker(pid_path, interval=60):
    """FTC main function.

    This function will check and enqueue scheduled jobs
    when the running time will come. After that sleep
    for `interval` seconds and repeat.
    """

    from DanceCat import app, db, rdb
    from .Models import Schedule, TrackJobRun
    from .JobWorker import job_worker_query

    def exit_handler(*args):
        """Clean up before quiting the process."""
        if len(args) > 0:
            print("Exit py signal {signal}".format(signal=args[0]))
        print(remove(pid_path))
        sys.exit()

    atexit.register(exit_handler)
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    while True:
        timer = Helpers.Timer()

        current_time = datetime.datetime.now()
        if current_time.second < 2:
            fq_sleep(2)
        print(
            "[FQ] Checking and scheduling at {start_time}".
            format(start_time=current_time)
        )

        next_schedules = Schedule.query.filter(
            Schedule.is_active,
            Schedule.next_run >= current_time,
            Schedule.next_run < current_time + relativedelta(seconds=interval)
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
                        ttl=900,
                        result_ttl=app.config.get(
                            'JOB_RESULT_VALID_SECONDS', 86400
                        ),
                        job_id="{tracker_id}".format(
                            tracker_id=tracker.track_job_run_id
                        )
                    )

                next_schedule.update_next_run(
                    validated=True,
                    interval=interval)
                db.session.commit()

        fq_sleep(interval - timer.get_total_seconds())

    exit_handler()


def start(interval=60, pid_path='frequency.pid'):
    """
    Check and start frequency_checker process if it not started.

    :param interval: Seconds the checker will sleep throughout idle time.
    :param pid_path: Location of the PID file.
    """
    try:
        pid_file = open(pid_path, 'r')
        pid = int(pid_file.read())
        print(
            "Frequency Task Checker is already started with pid {pid}".
            format(pid=pid)
        )
        pid_file.close()
    except (IOError, TypeError):
        process = Process(
            target=frequency_checker,
            kwargs={'pid_path': pid_path, 'interval': interval}
        )
        process.start()
        pid_file = open(pid_path, 'w')
        pid_file.write("{pid}".format(pid=process.pid))
        pid_file.close()
        print(
            "Start new Frequency Task Checker process with pid {pid}".
            format(pid=process.pid)
        )
