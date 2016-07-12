"""
Docstring for DanceCat.FrequencyTaskChecker(FTC) module.

This module will be used to check the schedule and
enqueue the next running job into the queue.
"""

import time
import atexit
import signal
import sys
from multiprocessing import Process
from os import remove


def frequency_checker(pid_path, feq=60):
    """
    FTC main function.

    This function will check and enqueue scheduled jobs
    when the running time will come. After that sleep
    for `feq` seconds and repeat.
    """
    # TODO: sleep if not enough time to cover lost time.

    def exit_handler(*args):
        """Clean up before quiting the process."""
        if len(args) > 0:
            print "Exit py signal {signal}".format(signal=args[0])
        remove(pid_path)
        sys.exit()

    atexit.register(exit_handler)
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    while True:
        print "From frequency checker!"
        time.sleep(feq)

    exit_handler()


def start(feq=60, pid_path='frequency.pid'):
    """
    Check and start frequency_checker process if it not started.

    :param feq: Seconds the checker will sleep throughout idle time.
    :param pid_path: Location of the PID file.
    """
    try:
        pid_file = open(pid_path, 'r')
        pid = int(pid_file.read())
        print "Frequency Task Checker is started with pid %d" % pid
        pid_file.close()
    except (IOError, TypeError):
        process = Process(target=frequency_checker, kwargs={'pid_path': pid_path, 'feq': feq})
        process.start()
        pid_file = open(pid_path, 'w')
        pid_file.write("%d" % process.pid)
        pid_file.close()
        print "Start a Frequency Task Checker process with pid=%d" % process.pid
