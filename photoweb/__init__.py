#!/usr/bin/env python

import json
import os
import shutil
import sys

from PIL import Image, ExifTags, IptcImagePlugin
import pystache

__version__ = "0.4.1"


class PhotoWebber:
    """
    Takes photo directories and creates HTML.
    """

    # Where to look for templates
    tpl_dir = os.path.expanduser("~/.photoweb/tpl")

    # The directory to store thumbnails in
    thumb_dirname = "thumbnails"

    # File extensions that we consider pictures
    pic_types = [".jpg", ".jpeg"]

    # encoding
    enc = "utf-8"

    IPTC_TAGS = {
        (2, 5): "ObjectName",
        (2, 120): "Caption",
    }

    def __init__(self, options):
        self.options = options
        self.tpl, self.tpl_md = self.load_tpl()

    def load_tpl(self):
        "Load the templates."
        tpl_name = self.options.template
        tpl = {}
        tpl_md = {}
        if not os.path.isdir(self.tpl_dir):
            self.create_default_tpl()
        tpl_path = os.path.join(self.tpl_dir, tpl_name)
        if not os.path.isdir(tpl_path):
            self.error(f"Can't find {tpl_name} template.")
        gallery_path = os.path.join(tpl_path, "gallery.html")
        detail_path = os.path.join(tpl_path, "detail.html")
        tpl_md_path = os.path.join(tpl_path, "md.json")
        if not os.path.exists(gallery_path):
            self.error(f"Can't find gallery.html in {tpl_name} template.")
        try:
            with open(gallery_path, "r", encoding=self.enc) as file_handle:
                tpl["gallery"] = file_handle.read()
        except IOError as why:
            self.error(f"Problem loading gallery template: {why}")
        if os.path.exists(detail_path):
            try:
                with open(detail_path, "r", encoding=self.enc) as file_handle:
                    tpl["detail"] = file_handle.read()
            except IOError as why:
                self.error(f"Problem loading detail template: {why}")
        if os.path.exists(tpl_md_path):
            try:
                with open(tpl_md_path, "r", encoding=self.enc) as tpl_md_fd:
                    tpl_md = json.load(tpl_md_fd)
            except (IOError, ValueError) as why:
                self.error(f"Problem loading template metadata: {why}")
        return tpl, tpl_md

    def create_default_tpl(self):
        "Create the default templates."
        default_tpl = os.path.join(os.path.dirname(__file__), "tpl-default")
        shutil.copytree(default_tpl, os.path.join(self.tpl_dir, "default"))

    def write_md(self, photo_dir, md_j):
        "Write the gallery metadata."
        md_file = os.path.join(photo_dir, "md.json")
        try:
            with open(md_file, "w", encoding=self.enc) as md_fd:
                json.dump(md_j, md_fd)
        except IOError as why:
            self.error(f"Couldn't write metatadata: {why}")

    def read_md(self, photo_dir):
        "Read the gallery metadata."
        md_file = os.path.join(photo_dir, "md.json")
        try:
            with open(md_file, "r", encoding=self.enc) as md_fd:
                md_j = json.load(md_fd)
        except (IOError, ValueError):
            md_j = {}
        # update with command-line options, if any
        if self.options.page_title:
            md_j["page_title"] = self.options.page_title.decode(self.enc)
        if self.options.page_desc:
            md_j["page_desc"] = [
                {"p": d.decode(self.enc)} for d in self.options.page_desc
            ]
        if self.options.reverse:
            md_j["reverse"] = True
        return md_j

    def run(self, photo_dir):
        "Process the photos in photo_dir."
        if not os.path.isdir(photo_dir):
            self.error(f"Can't find {photo_dir}")
        sys.stdout.write(f"Running {photo_dir}\n")

        md_j = self.read_md(photo_dir)
        page_vars = self.get_sorted_pics(photo_dir, md_j)
        pics = page_vars["pics"]
        # TODO: error if no pics found.

        # make the thumbnails
        if self.tpl_md.get("thumbnails", False):
            for pic in pics:
                pic["th_w"], pic["th_h"] = self.make_thumbnail(photo_dir, pic)

        page_vars.update(md_j)
        self.create_columns(pics, page_vars)

        # write gallery HTML
        gallery_html = pystache.render(self.tpl["gallery"], page_vars)
        gallery_html_path = os.path.join(photo_dir, "index.html")
        try:
            with open(gallery_html_path, "w", encoding=self.enc) as gal_fd:
                gal_fd.write(gallery_html)
        except IOError as why:
            self.error(f"Can't write gallery: {why}")

        # write detail pages
        if self.tpl.get("detail", False):
            for pic in pics:
                num = pic["num"]
                if num > 1:
                    pic["prev"] = pics[num - 2]["detail_path"]
                if pic["num"] < len(pics):
                    pic["next"] = pics[num]["detail_path"]
                    pic["next_img"] = pics[num]["img_path"]
                pic.update(md_j)
                detail_html = pystache.render(self.tpl["detail"], pic)
                detail_html_path = os.path.join(photo_dir, pic["detail_path"])
                try:
                    with open(detail_html_path, "w", encoding=self.enc) as detail_fd:
                        detail_fd.write(detail_html)
                except IOError as why:
                    self.error(f"Can't write detail page: {why}")

        self.write_md(photo_dir, md_j)

    def create_columns(self, pics, page_vars):
        "Create columns in the pae vars."
        if self.tpl_md.get("columns", False):
            pic_rows = []
            stops = range(0, len(pics), self.tpl_md["columns"])
            last_stop = 0
            for stop in stops[1:]:
                pic_rows.append({"pics": pics[last_stop:stop]})
                last_stop = stop
            if len(pics) > last_stop:
                pic_rows.append({"pics": pics[last_stop : len(pics)]})
            page_vars["pic_rows"] = pic_rows
            page_vars["columns"] = self.tpl_md["columns"]

    def make_thumbnail(self, photo_dir, pic):
        "Make a thumnail."
        thumb_dir = os.path.join(photo_dir, self.thumb_dirname)
        if not os.path.exists(thumb_dir):
            os.mkdir(thumb_dir)
        img_path = os.path.join(photo_dir, pic["img_path"])
        thumb_path = os.path.join(thumb_dir, pic["img_path"])
        image = Image.open(img_path)
        width = self.tpl_md.get("thumbnail_w", 250)
        height = self.tpl_md.get("thumbnail_h", 250)
        image.thumbnail((width, height), Image.Resampling.LANCZOS)
        image.save(thumb_path, "JPEG")
        return image.size

    def get_sorted_pics(self, photo_dir, md):
        "Get the pics and sort them"
        pics = self.load_pics(photo_dir)
        pics.sort(key=lambda x: x["date"])
        if md.get("reverse", False):
            pics.reverse()
        for i, pic in enumerate(pics):
            pic["num"] = i + 1
        page_vars = {
            "pics": pics,
        }
        return page_vars

    @staticmethod
    def sort_pics(pic_a, pic_b):
        "Sort function for pictures, by date."
        return (pic_a["date"] > pic_b["date"]) - (pic_a["date"] < pic_b["date"])

    def load_pics(self, photo_dir):
        "Find the pictures in photo_dir."
        files = os.listdir(photo_dir)
        pics = []
        for phile in files:
            phile = os.path.join(photo_dir, phile)
            if os.path.splitext(phile)[1].lower() not in self.pic_types:
                continue
            md, (width, height) = self.mdget(phile)
            if md is None:
                return []
            path = os.path.split(phile)[1]
            pics.append(
                {
                    "img_path": path,
                    "detail_path": f"{os.path.splitext(path)[0]}.html",
                    "title": md.get("Iptc.ObjectName", b"").decode("utf-8"),
                    "caption": md.get("Iptc.Caption", b"").decode("utf-8"),
                    "date": md.get("Exif.DateTimeOriginal", ""),
                    "w": md.get("Exif.ExifImageWidth", width),
                    "h": md.get("Exif.ExifImageHeight", height),
                }
            )
        return pics

    @staticmethod
    def mdget(phile):
        try:
            im = Image.open(phile)
        except IOError as why:
            sys.stderr.write(f"Can't find metadata for {phile} ({why}).\n")
            return None
        out = {}
        exif_info = im.getexif() or {}
        for tag, value in exif_info.items():
            decoded = ExifTags.TAGS.get(tag, "unknown")
            out["Exif." + decoded] = value
        iptc_info = IptcImagePlugin.getiptcinfo(im) or {}
        for tag, value in iptc_info.items():
            decoded = PhotoWebber.IPTC_TAGS.get(tag, "unknown")
            out["Iptc." + decoded] = value
        return out, im.size

    @staticmethod
    def error(msg):
        "Something has gone horribly wrong."
        sys.stderr.write(f"FATAL: {msg}\n")
        sys.exit(1)
