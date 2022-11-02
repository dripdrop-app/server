import base64
import io
import mutagen
import os
import subprocess
import traceback
import uuid
from server.logging import logger
from server.models.api import MusicResponses
from typing import Union


class TagExtractorService:
    def read_tags(
        self,
        file: Union[str, bytes, None] = None,
        filename: str = ...,
    ):
        folder_id = str(uuid.uuid4())
        tag_path = os.path.join("tags", folder_id)
        try:
            try:
                os.mkdir("tags")
            except FileExistsError:
                logger.exception(traceback.format_exc())
            os.mkdir(tag_path)
            filepath = os.path.join(tag_path, filename)
            with open(filepath, "wb") as f:
                f.write(file)
            audio_file = mutagen.File(filepath)
            title = (
                audio_file.tags["TIT2"].text[0]
                if audio_file.tags.get("TIT2", None)
                else ""
            )
            artist = (
                audio_file.tags["TPE1"].text[0]
                if audio_file.tags.get("TPE1", None)
                else ""
            )
            album = (
                audio_file.tags["TALB"].text[0]
                if audio_file.tags.get("TALB", None)
                else ""
            )
            grouping = (
                audio_file.tags["TIT1"].text[0]
                if audio_file.tags.get("TIT1", None)
                else ""
            )
            imageKeys = list(
                filter(lambda key: key.find("APIC") != -1, audio_file.keys())
            )
            buffer = None
            mimeType = None
            if imageKeys:
                mimeType = audio_file[imageKeys[0]].mime
                buffer = io.BytesIO(audio_file[imageKeys[0]].data)
            subprocess.run(["rm", "-rf", tag_path])
            artwork_url = None
            if buffer:
                base64_string = base64.b64encode(buffer.getvalue()).decode()
                artwork_url = f"data:{mimeType};base64,{base64_string}"
            return MusicResponses.Tags(
                title=title,
                artist=artist,
                album=album,
                grouping=grouping,
                artwork_url=artwork_url,
            )
        except Exception:
            subprocess.run(["rm", "-rf", tag_path])
            logger.exception(traceback.format_exc())
            return MusicResponses.Tags(
                title=None, artist=None, album=None, grouping=None, artwork_url=None
            )


tag_extractor_service = TagExtractorService()
