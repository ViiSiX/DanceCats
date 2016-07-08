import time


class Timer(object):
    def __init__(self):
        self.start_time = time.time() * 1000

    def get_total_time(self):
        total_time = time.time() * 1000 - self.start_time
        if total_time >= 60000:
            return "%d minutes %d seconds" % (total_time / 60000, (total_time % 60000) / 1000)
        elif total_time >= 1000:
            return "%d seconds" % (total_time / 1000)
        else:
            return "%d milliseconds" % total_time

    def get_total_milliseconds(self):
        return time.time() * 1000 - self.start_time
