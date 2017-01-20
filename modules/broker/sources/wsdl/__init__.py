# -*- coding: utf-8 -*-

from suds.client import Client

from broker.sources import Source
from broker.sources.exceptions import WsdlConnectError


class Wsdl(Source):
    """
        Класс источника Wsdl
    """
    type_source = "wsdl"
    wsdl_client = None

    def __init__(self, *args, **kwargs):
        super(Wsdl, self).__init__(*args, **kwargs)
        init_params = self.source_model.init_params
        try:
            url = init_params.pop('url')
            self.wsdl_client = Client(url, **init_params)
        except KeyError as e:
            raise WsdlConnectError(
                u"В параметрах wsdl источника {} не указан 'url'"
                .format(self.__class__.__name__)
            )
