import os
import sys
from typing import Any, List

from .templates import TemplateManager
from .gallery import Gallery
from .exceptions import PhotoWebError
from .types import PageVars, PictureData, GalleryMetadata


class PhotoWebber:
    """
    Orchestrates the photo gallery generation.
    """

    thumb_dirname = "thumbnails"
    enc = "utf-8"

    def __init__(self, options: Any) -> None:
        self.options = options
        self.templates = TemplateManager(options.template)

    def create_default_tpl(self) -> None:
        "Expose template creation to CLI."
        msg = self.templates.create_default_tpl()
        sys.stdout.write(f"{msg}\n")

    def run(self, photo_dir: str) -> None:
        "Process the photos in a directory."
        if not os.path.isdir(photo_dir):
            raise PhotoWebError(f"Can't find directory {photo_dir}")
        sys.stdout.write(f"Running {photo_dir}\n")

        gallery = Gallery(photo_dir, self.options)
        pics = gallery.load_pictures()
        if not pics:
            raise PhotoWebError(f"No pictures found in {photo_dir}")

        self._make_thumbnails(photo_dir, gallery)

        page_vars: PageVars = {
            "pics": pics,
            **gallery.md,
        }

        # handle columns
        columns = self.templates.tpl_md.get("columns", 0)
        if columns > 0:
            page_vars["pic_rows"] = gallery.create_rows(pics, columns)
            page_vars["columns"] = columns

        self._write_gallery(photo_dir, page_vars)
        self._write_details(photo_dir, pics, gallery.md)

        gallery.save_metadata()

    def _make_thumbnails(self, photo_dir: str, gallery: Gallery) -> None:
        if not self.templates.tpl_md.get("thumbnails", False):
            return
        thumb_dir = os.path.join(photo_dir, self.thumb_dirname)
        if not os.path.exists(thumb_dir):
            os.mkdir(thumb_dir)
        for pic in gallery.pictures:
            pic.data["th_w"], pic.data["th_h"] = pic.make_thumbnail(
                thumb_dir, self.templates.tpl_md
            )

    def _write_gallery(self, photo_dir: str, page_vars: PageVars) -> None:
        gallery_html = self.templates.render("gallery", page_vars)
        gallery_path = os.path.join(photo_dir, "index.html")
        try:
            with open(gallery_path, "w", encoding=self.enc) as gal_fd:
                gal_fd.write(gallery_html)
        except IOError as why:
            raise PhotoWebError(f"Can't write gallery: {why}") from why

    def _write_details(self, photo_dir: str, pics: List[PictureData], md: GalleryMetadata) -> None:
        if "detail" not in self.templates.tpl:
            return
        for i, pic_data in enumerate(pics):
            if pic_data["num"] > 1:
                pic_data["prev"] = pics[i - 1]["detail_path"]
            if pic_data["num"] < len(pics):
                pic_data["next"] = pics[i + 1]["detail_path"]
                pic_data["next_img"] = pics[i + 1]["img_path"]
            pic_data.update(md)
            detail_html = self.templates.render("detail", pic_data)
            detail_path = os.path.join(photo_dir, pic_data["detail_path"])
            try:
                with open(detail_path, "w", encoding=self.enc) as detail_fd:
                    detail_fd.write(detail_html)
            except IOError as why:
                raise PhotoWebError(f"Can't write detail page: {why}") from why
