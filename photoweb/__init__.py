#!/usr/bin/env python

"""
photoweb - Templated HTML galleries based on in-photo metadata.
"""

__author__ = "Mark Nottingham <mnot@mnot.net>"
__copyright__ = """\
Copyright (c) 2011-2012 Mark Nottingham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import json
from optparse import OptionParser
import os
import shutil
import sys

import Image
import pyexiv2
import pystache

__version__ = '0.2'



class PhotoWebber(object):
    """
    Takes photo directories and creates HTML.
    """

    # Where to look for templates
    tpl_dir = os.path.expanduser("~/.photoweb/tpl")

    # The directory to store thumbnails in
    thumb_dirname = "thumbnails"

    # File extensions that we consider pictures
    pic_types = ['.jpg', '.jpeg']

    # encoding
    enc = 'utf-8'

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
            self.error("Can't find %s template." % tpl_name)
        gallery_path = os.path.join(tpl_path, "gallery.html")
        detail_path = os.path.join(tpl_path, "detail.html")
        tpl_md_path = os.path.join(tpl_path, "md.json")
        if not os.path.exists(gallery_path):
            self.error("Can't find gallery.html in %s template." % tpl_name)
        try:
            tpl['gallery'] = open(gallery_path).read()
        except IOError, why:
            self.error("Problem loading gallery template: %s" % why)
        if os.path.exists(detail_path):
            try:
                tpl['detail'] = open(detail_path).read()
            except IOError, why:
                self.error("Problem loading detail template: %s" % why)
        if os.path.exists(tpl_md_path):
            try:
                tpl_md_fd = open(tpl_md_path, 'r')
                tpl_md = json.load(tpl_md_fd)
            except (IOError, ValueError), why:
                self.error("Problem loading template metadata: %s" % why)
            finally:
                tpl_md_fd.close()
        return tpl, tpl_md

    def create_default_tpl(self):
        "Create the default templates."
        default_tpl = os.path.join(os.path.dirname(__file__), 'tpl-default')
        shutil.copytree(default_tpl, os.path.join(self.tpl_dir, 'default'))

    def write_md(self, photo_dir, md_j):
        "Write the gallery metadata."
        md_file = os.path.join(photo_dir, 'md.json')
        try:
            md_fd = open(md_file, 'w')
            json.dump(md_j, md_fd)
        except IOError, why:
            self.error("Couldn't write metatadata: %s" % why)
        finally:
            md_fd.close()

    def read_md(self, photo_dir):
        "Read the gallery metadata."
        md_file = os.path.join(photo_dir, 'md.json')
        try:
            md_fd = open(md_file, 'r')
            md_j = json.load(md_fd)
            md_fd.close()
        except (IOError, ValueError):
            md_j = {}
        # update with command-line options, if any
        if self.options.page_title:
            md_j['page_title'] = self.options.page_title.decode(self.enc)
        if self.options.page_desc:
            md_j['page_desc'] = [
              {'p': d.decode(self.enc)} for d in self.options.page_desc
            ]
        return md_j

    def run(self, photo_dir):
        "Process the photos in photo_dir."
        if not os.path.isdir(photo_dir):
            self.error("Can't find %s" % photo_dir)
        sys.stdout.write("Running %s\n" % photo_dir)

        pics, page_vars = self.get_sorted_pics(photo_dir)
        md_j = self.read_md(photo_dir)
        page_vars.update(md_j)
        self.create_columns(pics, page_vars)

        # write gallery HTML
        gallery_html = pystache.render(self.tpl['gallery'], page_vars)
        gallery_html_path = os.path.join(photo_dir, "index.html")
        try:
            gal_fd = open(gallery_html_path, 'w')
            gal_fd.write(gallery_html.encode(self.enc))
        except IOError, why:
            self.error("Can't write gallery: %s" % why)
        finally:
            gal_fd.close()

        # make the thumbnails
        if self.tpl_md.get('thumbnails', False) and not self.options.html:
            for pic in pics:
                self.make_thumbnail(photo_dir, pic)

        # write detail pages
        if self.tpl.get('detail', False):
            for pic in pics:
                num = pic['num']
                if num > 1:
                    pic['prev'] = pics[num - 2]['detail_path']
                if pic['num'] < len(pics):
                    pic['next'] = pics[num]['detail_path']
                    pic['next_img'] = pics[num]['img_path']
                pic.update(md_j)
                detail_html = pystache.render(self.tpl['detail'], pic)
                detail_html_path = os.path.join(photo_dir, pic['detail_path'])
                try:
                    detail_fd = open(detail_html_path, 'w')
                    detail_fd.write(detail_html.encode(self.enc))
                except IOError, why:
                    self.error("Can't write detail page: %s" % why)
                finally:
                    detail_fd.close()

        self.write_md(photo_dir, md_j)

    def create_columns(self, pics, page_vars):
        "Create columns in the pae vars."
        if self.tpl_md.get('columns', False):
            pic_rows = []
            stops = range(0, len(pics), self.tpl_md['columns'])
            last_stop = 0
            for stop in stops[1:]:
                pic_rows.append({'pics': pics[last_stop:stop]})
                last_stop = stop
            if len(pics) > last_stop:
                pic_rows.append({'pics': pics[last_stop:len(pics)]})
            page_vars["pic_rows"] = pic_rows
            page_vars['columns'] = self.tpl_md['columns']

    def make_thumbnail(self, photo_dir, pic):
        "Make a thumnail."
        thumb_dir = os.path.join(photo_dir, self.thumb_dirname)
        if not os.path.exists(thumb_dir):
            os.mkdir(thumb_dir)
        img_path = os.path.join(photo_dir, pic['img_path'])
        thumb_path = os.path.join(thumb_dir, pic['img_path'])
        image = Image.open(img_path)
        width = self.tpl_md.get('thumbnail_w', 250)
        height = self.tpl_md.get('thumbnail_h', 250)
        image.thumbnail((width, height), Image.ANTIALIAS)
        image.save(thumb_path, "JPEG")

    def get_sorted_pics(self, photo_dir):
        "Get the pics and sort them"
        pics = self.load_pics(photo_dir)
        pics.sort(self.sort_pics)
        for i in range(len(pics)):
            pics[i]['num'] = i + 1
        page_vars = {
            'pics': pics,
        }
        return pics, page_vars
        
    @staticmethod
    def sort_pics(pic_a, pic_b):
        "Sort function for pictures, by date."
        return cmp(pic_a['date'], pic_b['date'])

    def load_pics(self, photo_dir):
        "Find the pictures in photo_dir."
        files = os.listdir(photo_dir)
        pics = []
        for phile in files:
            phile = os.path.join(photo_dir, phile)
            if os.path.splitext(phile)[1].lower() not in self.pic_types:
                continue
            try:
                md_i = pyexiv2.ImageMetadata(phile)
                md_i.read()
            except IOError, why:
                sys.stderr.write("Can't find metadata for %s (%s).\n" %
                    (phile, why)
                )
                continue
            def mdget(key, default=''):
                "Get metadata for key."
                try:
                    val = md_i[key]
                    if val.__class__ == pyexiv2.iptc.IptcTag:
                        return unicode(str(val.value[0]), self.enc)
                    else:
                        return unicode(str(val.value), self.enc)
                except (KeyError, AttributeError):
                    return default
            path = os.path.split(phile)[1]
            pics.append({
                'img_path': path,
                'detail_path': "%s.html" % os.path.splitext(path)[0],
                'title': mdget('Iptc.Application2.ObjectName'),
                'caption': mdget('Iptc.Application2.Caption'),
                'date': mdget('Exif.Photo.DateTimeOriginal'),
                'w': mdget('Exif.Photo.PixelXDimension'),
                'h': mdget('Exif.Photo.PixelYDimension'),
            })
        return pics

    @staticmethod
    def error(msg):
        "Something has gone horribly wrong."
        sys.stderr.write("FATAL: %s\n" % msg)
        sys.exit(1)


def photoweb_cli():
    "Run command-line photoweb."
    usage   = "Usage: %prog [options] <dir>"
    version = "photoweb version %s" % __version__
    option_parser = OptionParser(usage=usage, version=version)
    option_parser.set_defaults(
        template='default',
        html=False,
    )
    option_parser.add_option(
        "-t",
        action="store",
        dest="template",
        help="template to use"
    )
    option_parser.add_option(
        "-p",
        action="store",
        dest="page_title",
        help="Set the page's title"
    )
    option_parser.add_option(
        "-d",
        action="append",
        dest="page_desc",
        help="Set the page's description"
    )
    option_parser.add_option(
        "--html",
        action="store_true",
        dest="html",
        help="Only generate HTML (not thumbnails)"
    )
    (options, args) = option_parser.parse_args()
    if len(args) < 1:
        option_parser.error("Please specify at least one directory.")

    try:
        photoweb = PhotoWebber(options)
        thisdir = os.getcwd()
        for photodir in args:
            photoweb.run(os.path.join(thisdir, photodir))
    except KeyboardInterrupt:
        photoweb.error("Interrupted.")


if __name__ == '__main__':
    photoweb_cli()
