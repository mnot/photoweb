========
Photoweb
========

Photoweb creates HTML galleries based on in-photo metadata, from flexible
templates. What's different about it?

* It's easy to add new photos; just drop them in the folder and re-run
* You don't have to track metadata; it comes from the photos themselves, using
  standard embedded metadata
* It's easy to modify the templates to make your photos look great.

See <http://www.mnot.net/photo/> for an example.


Installing Photoweb
-------------------

Photoweb needs:

1. Python 2.6 or greater; see <http://python.org/>
2. The PIL and pystache libraries.

It's easiest with PIP:

  $ pip install photoweb


Using Photoweb
--------------

To generate the HTML for a gallery, call photoweb from the command line:

  $ photoweb . 

You can generate multiple galleries at once:

  $ photoweb beach hawaii snow

When you first generate a gallery, you can specify the page title and
description, which will be used in the template:

  $ photoweb -p "At the Beach" -d "We went to the beach for a weekend. Fun!" . 

The page metadata will be saved in a file (md.json) for use next time you
run photoweb. 


Creating and Using Templates
----------------------------

By default, the default template will be used (from ~/.photoweb/tpl/default; 
if it isn't there, it'll be automagically created). You can edit this, or
create new templates, using them with the -t option:

  $ photoweb -t "my template" .

Templates are directories with the following files in them:

 * md.json - a configuration file
 * gallery.html - the overview page
 * detail.html - a single photo page
 
Take a look at the default template to get an idea of how to create your own.


License
-------

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