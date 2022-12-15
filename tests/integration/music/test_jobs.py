from ...conftest import APIEndpoints


class MusicJobEndpoints:
    base_url = f"{APIEndpoints.base_path}/music/jobs"
    jobs = f"{base_url}/1/1"
    listen = f"{base_url}/listen"
    create_youtube = f"{base_url}/create/youtube"
    create_file = f"{base_url}/create/file"
    delete_job = f"{base_url}/delete"
