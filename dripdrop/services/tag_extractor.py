import base64
import io
import mutagen.id3
import os
import re
import traceback
import uuid
from dripdrop.logging import logger
from dripdrop.music.responses import TagsResponse
from typing import Union, Optional


class TagExtractorService:
    _TAGS_FOLDER = "tags"
    _TITLE_TAG = "TIT2"
    _ARTIST_TAG = "TPE1"
    _ALBUM_TAG = "TALB"
    _GROUPING_TAG = "TIT1"
    _ARTWORK_TAG = "APIC:"

    def _create_folder(self):
        folder_id = str(uuid.uuid4())
        tag_path = os.path.join(TagExtractorService._TAGS_FOLDER, folder_id)
        try:
            os.mkdir("tags")
        except FileExistsError:
            logger.exception(traceback.format_exc())
        os.mkdir(tag_path)
        return tag_path

    def _get_tag(
        self, tags: mutagen.id3.ID3 = ..., tag_name: str = ...
    ) -> Optional[str]:
        tag = tags.get(tag_name)
        if tag:
            return tag.text[0]
        return None

    def _get_artwork_as_base64(self, tags: mutagen.id3.ID3 = ...) -> Optional[str]:
        buffer = None
        mime_type = None
        for tag_name in tags.keys():
            if re.match(TagExtractorService._ARTWORK_TAG, tag_name):
                tag = tags.get(tag_name)
                buffer = io.BytesIO(tag.data)
                mime_type = tag.mime
                base64_string = base64.b64encode(buffer.getvalue()).decode()
                return f"data:{mime_type};base64,{base64_string}"
        return None

    def _clean_up(self, tag_path: str = ...):
        try:
            for item in os.scandir(tag_path):
                if os.path.isfile(item):
                    os.remove(item)
            os.removedirs(tag_path)
        except Exception:
            pass

    def read_tags(
        self,
        file: Union[str, bytes, None] = None,
        filename: str = ...,
    ):
        tag_path = self._create_folder()
        try:
            file_path = os.path.join(tag_path, filename)
            with open(file_path, "wb") as f:
                f.write(file)

            tags = mutagen.id3.ID3(file_path)
            title = self._get_tag(tags=tags, tag_name=TagExtractorService._TITLE_TAG)
            artist = self._get_tag(tags=tags, tag_name=TagExtractorService._ARTIST_TAG)
            album = self._get_tag(tags=tags, tag_name=TagExtractorService._ALBUM_TAG)
            grouping = self._get_tag(
                tags=tags, tag_name=TagExtractorService._GROUPING_TAG
            )
            artwork_url = self._get_artwork_as_base64(tags=tags)
            self._clean_up(tag_path=tag_path)
            return TagsResponse(
                title=title,
                artist=artist,
                album=album,
                grouping=grouping,
                artwork_url=artwork_url,
            )
        except Exception:
            self._clean_up(tag_path=tag_path)
            logger.exception(traceback.format_exc())
            return TagsResponse()


tag_extractor_service = TagExtractorService()
