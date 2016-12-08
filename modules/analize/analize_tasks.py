# -*- coding: utf-8 -*-

from app_celery.analize import app

from celery.utils.log import get_task_logger

from brocker.sourses import DataBaseSourse, FileSourse


logger = get_task_logger(__name__)

@app.task(name="run")
def run_task():
    print "in run_task"
    dbs = DataBaseSourse()
    # dbs.f1()
    callbacks = DataBaseSourse.get_all_callbacks()
    callbacks[0](dbs)

    # f = FileSourse()
    # f.f2_()
    return


@app.task(name="hello")
def fun1():
    print "analize callback"

