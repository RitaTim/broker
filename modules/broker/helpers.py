# -*- coding: utf-8 -*-


def get_db_allias_for_source(source_name):
    """
        Возварщает алиас бд источника
    """
    return "{}_source".format(source_name.lower())
