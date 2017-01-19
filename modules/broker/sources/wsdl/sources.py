# -*- coding: utf-8 -*-

from broker.sources import Source


class Wsdl(Source):
    """
        Класс источника Wsdl
    """
    type_source = "wsdl"

    def __init__(self, *args, **kwargs):
        super(Wsdl, self).__init__(*args, **kwargs)
