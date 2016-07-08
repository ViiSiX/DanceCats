import time
import atexit
import signal
import sys
from multiprocessing import Process
from os import remove


def frequency_checker(pid_path, f=10):
    def exit_handler(*args):
        if len(args) > 0:
            print "Exit py signal {signal}".format(signal=args[0])
        remove(pid_path)
        sys.exit()

    atexit.register(exit_handler)
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    while True:
        print "From frequency checker!"
        time.sleep(f)

    exit_handler()


def start(f=10, pid_path='frequency.pid'):
    try:
        pid_file = open(pid_path, 'r')
        pid = int(pid_file.read())
        print "Frequency Task Checker is started with pid %d" % pid
        pid_file.close()
    except (IOError, TypeError):
        p = Process(target=frequency_checker, kwargs={'pid_path': pid_path, 'f': f})
        p.start()
        pid_file = open(pid_path, 'w')
        pid_file.write("%d" % p.pid)
        pid_file.close()
        print "Start a Frequency Task Checker process with pid=%d" % p.pid
