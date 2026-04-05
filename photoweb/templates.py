import json
import os
import shutil
from typing import Tuple, Literal, Mapping, Any

import jinja2

from .types import TemplateMetadata, TemplateData
from .exceptions import PhotoWebError


class TemplateManager:
    """
    Manages loading and rendering templates.
    """

    # Where to look for user templates
    tpl_dir = os.path.expanduser("~/.photoweb/tpl")

    # Bundled templates
    pkg_tpl_dir = os.path.join(os.path.dirname(__file__), "templates")

    # encoding
    enc = "utf-8"

    def __init__(self, tpl_name: str) -> None:
        self.tpl_name = tpl_name
        self.tpl_path: str = ""
        self.tpl, self.tpl_md = self.load_tpl()

    def load_tpl(self) -> Tuple[TemplateData, TemplateMetadata]:
        "Load the templates."
        tpl: TemplateData = {}
        tpl_md: TemplateMetadata = {}

        if self.tpl_name == "default":
            # first check for a user-specified default
            tpl_path = os.path.join(self.tpl_dir, self.tpl_name)
            if not os.path.isdir(tpl_path):
                # use the package default
                tpl_path = self.pkg_tpl_dir
        else:
            tpl_path = os.path.join(self.tpl_dir, self.tpl_name)

        self.tpl_path = tpl_path

        if not os.path.isdir(tpl_path):
            raise PhotoWebError(f"Can't find {self.tpl_name} template.")

        gallery_path = os.path.join(tpl_path, "gallery.html")
        detail_path = os.path.join(tpl_path, "detail.html")
        tpl_md_path = os.path.join(tpl_path, "md.json")

        if not os.path.exists(gallery_path):
            raise PhotoWebError(f"Can't find gallery.html in {self.tpl_name} template.")

        try:
            with open(gallery_path, "r", encoding=self.enc) as file_handle:
                tpl["gallery"] = file_handle.read()
        except IOError as why:
            raise PhotoWebError(f"Problem loading gallery template: {why}") from why

        if os.path.exists(detail_path):
            try:
                with open(detail_path, "r", encoding=self.enc) as file_handle:
                    tpl["detail"] = file_handle.read()
            except IOError as why:
                raise PhotoWebError(f"Problem loading detail template: {why}") from why

        if os.path.exists(tpl_md_path):
            try:
                with open(tpl_md_path, "r", encoding=self.enc) as tpl_md_fd:
                    tpl_md = json.load(tpl_md_fd)
            except (IOError, ValueError) as why:
                raise PhotoWebError(
                    f"Problem loading template metadata: {why}"
                ) from why

        return tpl, tpl_md

    def render(
        self, tpl_type: Literal["gallery", "detail"], data: Mapping[str, Any]
    ) -> str:
        "Render a template with data."
        if tpl_type not in self.tpl:
            raise PhotoWebError(f"Template type {tpl_type} not found.")
        tpl = jinja2.Template(self.tpl[tpl_type])
        return tpl.render(data)

    def create_default_tpl(self) -> str:
        "Create the default templates."
        dest_dir = os.path.join(self.tpl_dir, "default")
        if os.path.isdir(dest_dir):
            return "Default templates already exist."
        shutil.copytree(self.pkg_tpl_dir, dest_dir)
        return f"Default templates copied to {dest_dir}"
