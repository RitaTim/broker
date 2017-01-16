# -*- coding: utf-8 -*-

from functools import wraps

from broker.sources import TransactionAtomicManager


def transaction_atomic(func):
    """
        Отключает autocommit на время выполнения функции
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with TransactionAtomicManager(self.connector):
            func(self, *args, **kwargs)
    return wrapper
