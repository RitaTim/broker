# -*- coding: utf-8 -*-

from app_celery.analize import app

from celery.utils.log import get_task_logger



logger = get_task_logger(__name__)

@app.task(name="run")
def run_task():
    print "in run_task"


@app.task(name="hello")
def fun1():
    print "analize callback"

