from typing import Any, Awaitable, Dict, List, Union

from stream_chat.base.query_threads import QueryThreadsInterface
from stream_chat.types.stream_response import StreamResponse


class QueryThreads(QueryThreadsInterface):
    def query_threads(
        self,
        filter: Dict[str, Dict[str, Any]],
        sort: List[Dict[str, Any]],
        **options: Any,
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        payload = {"filter": filter, "sort": sort, **options}
        return self.client.post(self.url, data=payload)
