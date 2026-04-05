from typing import TypedDict, List, Dict


class PictureData(TypedDict, total=False):
    img_path: str
    detail_path: str
    title: str
    caption: str
    date: str
    w: int  # pylint: disable=invalid-name
    h: int  # pylint: disable=invalid-name
    num: int
    th_w: int
    th_h: int
    prev: str
    next: str
    next_img: str


class GalleryMetadata(TypedDict, total=False):
    page_title: str
    page_desc: List[Dict[str, str]]
    reverse: bool


class TemplateMetadata(TypedDict, total=False):
    thumbnails: bool
    columns: int
    thumbnail_w: int
    thumbnail_h: int


class TemplateData(TypedDict, total=False):
    gallery: str
    detail: str


class PicRow(TypedDict):
    pics: List[PictureData]


class PageVars(GalleryMetadata, total=False):
    pics: List[PictureData]
    pic_rows: List[PicRow]
    columns: int
