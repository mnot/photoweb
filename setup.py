#!/usr/bin/env python

from distutils.core import setup
import photoweb

setup(
  name = 'photoweb',
  version = photoweb.__version__,
  description = 'Templated HTML galleries based on in-photo metadata',
  author = 'Mark Nottingham',
  author_email = 'mnot@mnot.net',
  url = 'http://github.com/mnot/photoweb/',
  download_url = \
    'http://github.com/mnot/photoweb/tarball/%s' % photoweb.__version__,
  packages=['photoweb'],
  package_dir={'photoweb':'photoweb'},
  scripts=['bin/photoweb'],
  package_data={'photoweb': ['tpl-default/*']},
  install_requires = [
    "PIL",
    "pyexiv2",
    "pystache"
  ],
  long_description=open("README.rst").read(),
  classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Other Audience',
    'License :: OSI Approved :: MIT License',
    'Environment :: Console',
    'Programming Language :: Python',
    'Operating System :: POSIX',
    'Topic :: Text Processing :: Markup :: HTML',
    'Topic :: Multimedia :: Graphics :: Presentation',
  ]
)