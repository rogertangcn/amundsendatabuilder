import importlib
from typing import Iterator, Any  # noqa: F401

from pyhocon import ConfigTree  # noqa: F401

from databuilder.extractor.base_extractor import Extractor
from databuilder.rest_api.base_rest_api_query import BaseRestApiQuery


REST_API_QUERY = 'restapi_query'
MODEL_CLASS = 'model_class'


class RestAPIExtractor(Extractor):
    """
    An Extractor that calls one or more REST API to extract the data.
    This extractor almost entirely depends on RestApiQuery.
    """


    def init(self, conf):
        # type: (ConfigTree) -> None
        self._restapi_query = conf.get(REST_API_QUERY)  # type: BaseRestApiQuery
        self._iterator = None  # type: Iterator[Dict[str, Any]]

        model_class = conf.get(MODEL_CLASS, None)
        if model_class:
            module_name, class_name = model_class.rsplit(".", 1)
            mod = importlib.import_module(module_name)
            self.model_class = getattr(mod, class_name)



    def extract(self):
        # type: () -> Any
        """
        Fetch one result row from RestApiQuery, convert to {model_class} if specified before
        returning.
        :return:
        """

        if not self._iterator:
            self._iterator = self._restapi_query.execute()

        try:
            record = next(self._iterator)
        except StopIteration:
            return None

        if hasattr(self, 'model_class'):
            return self.model_class(**record)

        return record

    def get_scope(self):
        # type: () -> str
        return 'extractor.restapi'