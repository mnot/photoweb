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

from optparse import OptionParser
import os

from . import PhotoWebber

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
        "-r",
        action="store_true",
        dest="reverse",
        help="Reverse the order of the photos"
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