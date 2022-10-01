from fastapi.routing import APIRoute
from fastapi import Request, Response
from typing import Callable
import json
import dicttoxml


async def do_or_error(
    to_be_called, request
):
    response = await to_be_called(request)
    if request.headers.get("media-type") == "application/xml":
        data = json.loads(response.body)
        xml_data = dicttoxml.dicttoxml(data)
        return Response(content=xml_data, media_type="application/xml")
    return response


class Wrapper(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            return await do_or_error(
                to_be_called=original_route_handler,
                request=request,
            )
        return custom_route_handler
