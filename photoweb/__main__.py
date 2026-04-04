#!/usr/bin/env python

from optparse import OptionParser
import os

from . import PhotoWebber, __version__


def photoweb_cli() -> None:
    "Run command-line photoweb."
    usage = "Usage: %prog [options] <dir>"
    version = f"photoweb version {__version__}"
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
    option_parser.add_option(
        "-c",
        "--copy-templates",
        action="store_true",
        dest="copy_templates",
        help="Copy the default templates to ~/.photoweb/tpl/default",
    )
    options, args = option_parser.parse_args()
    if len(args) < 1 and not options.copy_templates:
        option_parser.error("Please specify at least one directory.")

    try:
        photoweb = PhotoWebber(options)
        if options.copy_templates:
            photoweb.create_default_tpl()
        else:
            thisdir = os.getcwd()
            for photodir in args:
                photoweb.run(os.path.join(thisdir, photodir))
    except KeyboardInterrupt:
        photoweb.error("Interrupted.")
