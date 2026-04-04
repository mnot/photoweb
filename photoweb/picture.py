import os
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

from PIL import Image, ExifTags, IptcImagePlugin, ImageOps

from .types import PictureData, TemplateMetadata


class Picture:
    """
    Represents a single photo.
    """

    # File extensions that we consider pictures
    pic_types = [".jpg", ".jpeg"]

    # IPTC tags to decode
    IPTC_TAGS = {
        (2, 5): "ObjectName",
        (2, 105): "Headline",
        (2, 120): "Caption",
    }

    def __init__(self, photo_path: str) -> None:
        self.photo_path = photo_path
        self.filename = os.path.basename(photo_path)
        self.data: PictureData = {}
        self.md, (self.width, self.height) = self._get_metadata()

    def _get_metadata(self) -> Tuple[Optional[Dict[str, Any]], Tuple[int, int]]:
        try:
            with Image.open(self.photo_path) as im:
                out: Dict[str, Any] = {}
                exif_obj = im.getexif()
                # main EXIF tags (IFD0)
                for tag, value in exif_obj.items():
                    decoded = ExifTags.TAGS.get(tag, "unknown")
                    out["Exif." + decoded] = value

                # standard EXIF SubIFD (often contains DateTimeOriginal)
                sub_ifd = exif_obj.get_ifd(ExifTags.Base.ExifOffset)
                for sub_tag, sub_value in sub_ifd.items():
                    decoded = ExifTags.TAGS.get(sub_tag, "unknown")
                    out["Exif." + decoded] = sub_value

                iptc_info = IptcImagePlugin.getiptcinfo(im) or {}
                for iptc_tag, iptc_value in iptc_info.items():
                    decoded = self.IPTC_TAGS.get(iptc_tag, "unknown")
                    out["Iptc." + decoded] = iptc_value

                # XMP metadata (often contains dc:title)
                try:
                    xmp_info = im.getxmp()
                    for xmp_k, xmp_v in xmp_info.items():
                        out["Xmp." + str(xmp_k)] = xmp_v
                except (AttributeError, ValueError, TypeError):
                    # getxmp() may fail or not exist in some Pillow versions/configurations
                    pass

                # Get dimensions after accounting for orientation
                with ImageOps.exif_transpose(im) as oriented_im:
                    size = oriented_im.size
                return out, size
        except IOError:
            return None, (0, 0)

    def _get_val(self, key: str) -> str:
        "Get a string value from metadata, handling bytes, lists and dicts."
        if self.md is None:
            return ""
        val = self.md.get(key, "")
        if isinstance(val, (list, tuple)):
            if not val:
                return ""
            val = val[0]
        if isinstance(val, bytes):
            return val.decode("utf-8").strip()
        if isinstance(val, dict):
            # handle XMP Alt containers
            for xmp_val in val.values():
                if isinstance(xmp_val, str):
                    return xmp_val.strip()
        result = str(val).strip()
        if result == "unknown":
            return ""
        return result

    def process(self) -> PictureData:
        "Process metadata into common PictureData."
        if self.md is None:
            return {}

        date_str = self.md.get("Exif.DateTimeOriginal", "")
        try:
            date_obj = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
            formatted_date = date_obj.strftime("%-d %b %Y")
        except (ValueError, TypeError):
            formatted_date = date_str

        # Get title with fallback
        title = ""
        title_sources = [
            "Iptc.ObjectName",
            "Iptc.Headline",
            "Exif.XPTitle",
            "Xmp.dc:title",
        ]
        for source in title_sources:
            title = self._get_val(source)
            if title:
                break

        if not title:
            stem = os.path.splitext(self.filename)[0]
            ignore_prefixes = ["IMG_", "DSC_", "_MG_", "P_"]
            if not any(stem.upper().startswith(p) for p in ignore_prefixes):
                title = stem

        self.data = {
            "img_path": self.filename,
            "detail_path": f"{os.path.splitext(self.filename)[0]}.html",
            "title": title.strip(),
            "caption": self._get_val("Iptc.Caption"),
            "date": formatted_date,
            "w": self.width,
            "h": self.height,
        }
        return self.data

    def make_thumbnail(self, thumb_dir: str, tpl_md: TemplateMetadata) -> Tuple[int, int]:
        "Make a thumbnail."
        thumb_path = os.path.join(thumb_dir, self.filename)
        with Image.open(self.photo_path) as im:
            image = ImageOps.exif_transpose(im)
            width = tpl_md.get("thumbnail_w", 250)
            height = tpl_md.get("thumbnail_h", 250)
            image.thumbnail((width, height), Image.Resampling.LANCZOS)
            image.save(thumb_path, "JPEG")
            return image.size
