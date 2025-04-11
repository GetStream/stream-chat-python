import abc
from typing import Any, Awaitable, Dict, List, Union

from stream_chat.types.stream_response import StreamResponse


class QueryThreadsInterface(abc.ABC):
    def __init__(self):
        pass

    @property
    def url(self):
        return "threads"

    @abc.abstractmethod
    def query_threads(
        self,
        filter: Dict[str, Dict[str, Any]],
        sort: List[Dict[str, Any]],
        **options: Any,
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Get a list of threads given filter and sort options

        :param filter: filter conditions (e.g. {"created_by_user_id": {"$eq": "user_123"}})
        :param sort: sort options (e.g. [{"field": "last_message_at", "direction": -1}])
        :return: the Server Response
        """
        pass
