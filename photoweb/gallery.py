import json
import os
from typing import List, Any

from .types import GalleryMetadata, PictureData, PicRow
from .picture import Picture
from .exceptions import PhotoWebError


class Gallery:
    """
    Represents a photo gallery in a directory.
    """

    def __init__(self, photo_dir: str, options: Any) -> None:
        self.photo_dir = photo_dir
        self.options = options
        self.enc = "utf-8"
        self.md = self._load_metadata()
        self.pictures: List[Picture] = []

    def _load_metadata(self) -> GalleryMetadata:
        md_file = os.path.join(self.photo_dir, "md.json")
        try:
            with open(md_file, "r", encoding=self.enc) as md_fd:
                md_j: GalleryMetadata = json.load(md_fd)
        except (IOError, ValueError):
            md_j = {}

        if self.options.page_title:
            md_j["page_title"] = str(self.options.page_title)
        if self.options.page_desc:
            md_j["page_desc"] = [{"p": str(d)} for d in self.options.page_desc]
        if self.options.reverse:
            md_j["reverse"] = True
        return md_j

    def save_metadata(self) -> None:
        "Save gallery metadata to md.json."
        md_file = os.path.join(self.photo_dir, "md.json")
        try:
            with open(md_file, "w", encoding=self.enc) as md_fd:
                json.dump(self.md, md_fd)
        except IOError as why:
            raise PhotoWebError(f"Couldn't write metadata: {why}") from why

    def load_pictures(self) -> List[PictureData]:
        "Find and load pictures in the directory."
        files = os.listdir(self.photo_dir)
        pics_data: List[PictureData] = []
        for filename in files:
            phile_path = os.path.join(self.photo_dir, filename)
            if os.path.splitext(filename)[1].lower() not in Picture.pic_types:
                continue
            pic = Picture(phile_path)
            data = pic.process()
            if not data:
                continue
            self.pictures.append(pic)
            pics_data.append(data)

        # sort by date
        pics_data.sort(key=lambda x: x["date"])
        if self.md.get("reverse", False):
            pics_data.reverse()

        for i, pic_data in enumerate(pics_data):
            pic_data["num"] = i + 1
            pic_data["detail_path"] = f"{i + 1}.html"

        return pics_data

    @staticmethod
    def create_rows(pics: List[PictureData], columns: int) -> List[PicRow]:
        "Organize pictures into rows."
        pic_rows: List[PicRow] = []
        if columns <= 0:
            return []
        stops = range(0, len(pics), columns)
        last_stop = 0
        for stop in stops[1:]:
            pic_rows.append({"pics": pics[last_stop:stop]})
            last_stop = stop
        if len(pics) > last_stop:
            pic_rows.append({"pics": pics[last_stop : len(pics)]})
        return pic_rows
