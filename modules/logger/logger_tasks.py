# -*- coding: utf-8 -*-

from app_celery.logger import app

from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@app.task(name="hello")
def fun2():
    print "logger callback"
