#!/usr/bin/env python

from optparse import OptionParser
import os

from . import PhotoWebber


def photoweb_cli():
    "Run command-line photoweb."
    usage = "Usage: %prog [options] <dir>"
    version = "photoweb version %s" % __version__
    option_parser = OptionParser(usage=usage, version=version)
    option_parser.set_defaults(
        template="default",
        html=False,
    )
    option_parser.add_option(
        "-t", action="store", dest="template", help="template to use"
    )
    option_parser.add_option(
        "-p", action="store", dest="page_title", help="Set the page's title"
    )
    option_parser.add_option(
        "-d", action="append", dest="page_desc", help="Set the page's description"
    )
    option_parser.add_option(
        "-r",
        action="store_true",
        dest="reverse",
        help="Reverse the order of the photos",
    )
    options, args = option_parser.parse_args()
    if len(args) < 1:
        option_parser.error("Please specify at least one directory.")

    try:
        photoweb = PhotoWebber(options)
        thisdir = os.getcwd()
        for photodir in args:
            photoweb.run(os.path.join(thisdir, photodir))
    except KeyboardInterrupt:
        photoweb.error("Interrupted.")
