# -*- coding: utf-8 -*-


def is_signal(max_retries=1, expire=60, routing_key='default'):
    print "INIT SIGNAL"

    def decorator(func):
        def signal(self, *args, **kwargs):
            print "CALL SIGNAL"
            print "max_retries={}, expire={}, routing_key={}"\
                   .format(max_retries, expire, routing_key)
            func(self, *args, **kwargs)
        return signal
    return decorator


def is_callback(func):
    print "INIT CALLBACK"

    def callback(self, *args, **kwargs):
        print "CALL CALLBACK"
        return func(self, *args, **kwargs)
    return callback
