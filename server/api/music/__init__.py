from starlette.routing import Mount, Route, WebSocketRoute
from server.utils.enums import RequestMethods
from server.api.music.endpoints import (
    delete_job,
    download_job,
    get_artwork,
    listen_jobs,
    get_grouping,
    get_tags,
    download
)

routes = [
    Mount('/music', routes=[
        Route(
            '/getArtwork',
            endpoint=get_artwork,
            methods=[RequestMethods.GET.value]
        ),
        Route(
            '/grouping',
            endpoint=get_grouping,
            methods=[RequestMethods.GET.value]
        ),
        Route(
            '/getTags',
            endpoint=get_tags,
            methods=[RequestMethods.POST.value]
        ),
        Route(
            '/download',
            endpoint=download,
            methods=[RequestMethods.POST.value]
        ),
        Route(
            '/deleteJob',
            endpoint=delete_job,
            methods=[RequestMethods.GET.value]
        ),
        Route(
            '/downloadJob',
            endpoint=download_job,
            methods=[RequestMethods.GET.value]
        ),
        WebSocketRoute('/listenJobs', endpoint=listen_jobs),
    ])
]
