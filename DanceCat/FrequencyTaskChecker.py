from threading import Timer


def frequency_checker(f=1):
    print 'From frequency_checker with f = %d' % f

    Timer(f, frequency_checker, [f]).start()
