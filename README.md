# Photoweb

Photoweb creates HTML galleries based on in-photo metadata, from flexible
templates. What's different about it?

* It's easy to add new photos; just drop them in the folder and re-run
* You don't have to track metadata; it comes from the photos themselves, using
  standard embedded metadata
* It's easy to modify the templates to make your photos look great.


## Installing Photoweb

Photoweb needs:

1. Python 2.6 or greater; see <http://python.org/>
2. The PIL and pystache libraries.

It's easiest with PIP:

> pip install photoweb


## Using Photoweb

To generate the HTML for a gallery, call it from the command line:

> photoweb . 

You can generate multiple galleries at once:

> photoweb beach hawaii snow

When you first generate a gallery, you can specify the page title and
description, which will be used in the template:

> photoweb -p "At the Beach" -d "We went to the beach for a weekend. Fun!" . 

The page metadata will be saved in a file (md.json) for use next time you
run photoweb. 


## Creating and Using Templates

By default, the default template will be used (from `~/.photoweb/tpl/default`; 
if it isn't there, it'll be automagically created). You can edit this, or
create new templates, using them with the -t option:

> photoweb -t "my template" .

Templates are directories with the following files in them:

* md.json - a configuration file
* gallery.html - the overview page
* detail.html - a single photo page
 
Take a look at the default template to get an idea of how to create your own.

