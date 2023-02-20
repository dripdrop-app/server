import base64
import io
import mutagen.id3
import re


class AudioTags:
    _TITLE_TAG = "TIT2"
    _ARTIST_TAG = "TPE1"
    _ALBUM_TAG = "TALB"
    _GROUPING_TAG = "TIT1"
    _ARTWORK_TAG = "APIC:"

    def __init__(self, file_path: str = ...):
        self.tags = mutagen.id3.ID3(file_path)

    def _get_tag(self, tag_name: str = ...) -> str | None:
        tag = self.tags.get(tag_name)
        if tag:
            return tag.text[0]
        return None

    @property
    def title(self):
        return self._get_tag(tag_name=AudioTags._TITLE_TAG)

    @title.setter
    def title(self, value: str):
        self.tags.delall(AudioTags._TITLE_TAG)
        self.tags.add(mutagen.id3.TIT2(text=[value]))
        self.tags.save()

    @property
    def artist(self):
        return self._get_tag(tag_name=AudioTags._ARTIST_TAG)

    @artist.setter
    def artist(self, value: str):
        self.tags.delall(AudioTags._ARTIST_TAG)
        self.tags.add(mutagen.id3.TPE1(text=value))
        self.tags.save()

    @property
    def album(self):
        return self._get_tag(tag_name=AudioTags._ALBUM_TAG)

    @album.setter
    def album(self, value: str):
        self.tags.delall(AudioTags._ALBUM_TAG)
        self.tags.add(mutagen.id3.TALB(text=value))
        self.tags.save()

    @property
    def grouping(self):
        return self._get_tag(tag_name=AudioTags._GROUPING_TAG)

    @grouping.setter
    def grouping(self, value: str):
        self.tags.delall(AudioTags._GROUPING_TAG)
        self.tags.add(mutagen.id3.TIT1(text=value))
        self.tags.save()

    @property
    def artwork(self):
        for tag_name in self.tags.keys():
            if re.match(AudioTags._ARTWORK_TAG, tag_name):
                tag = self.tags.get(tag_name)
                return tag

    def set_artwork(self, data: bytes = ..., mime_type: str = ...):
        self.tags.delall(AudioTags._ARTWORK_TAG)
        self.tags.add(mutagen.id3.APIC(mime=mime_type, data=data))
        self.tags.save()

    def get_artwork_as_base64(self):
        tag = self.artwork
        if tag:
            buffer = io.BytesIO(tag.data)
            mime_type = tag.mime
            base64_string = base64.b64encode(buffer.getvalue()).decode()
            return f"data:{mime_type};base64,{base64_string}"
        return None
