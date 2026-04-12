# Photoweb

Photoweb creates HTML galleries based on in-photo metadata, using flexible
templates. What's different about it?

* It's easy to add new photos; just drop them in the folder and re-run.
* You don't have to track metadata; it comes from the photos themselves, using
  standard embedded metadata (EXIF, IPTC, XMP).
* **Automatic Optimization**: It can optimize your images for the web, stripping
  unnecessary metadata and using perceptual quality search to minimize file size.
* **Smart Orientation**: Automatically handles photo orientation (fixing rotated 
  images from phones/cameras).
* It includes specialized support for titles and descriptions from Apple Photos.
* It's easy to modify the templates to make your photos look great.
* It supports modern web features like dark mode, keyboard navigation, and 
  responsive side-by-side layouts out of the box.


## Installation

Photoweb needs [Python](https://www.python.org/).

It's easiest with [pipx](https://pipx.pypa.io/stable/):

> pipx install photoweb


## Usage

To generate the HTML for a gallery, call it from the command line:

> photoweb . 

You can generate multiple galleries at once:

> photoweb beach hawaii snow

When you first generate a gallery, you can specify the page title and
description, which will be used in the template:

> photoweb -p "At the Beach" -d "We went to the beach for a weekend. Fun!" . 

The page metadata will be saved in a file (md.json) for use next time you
run photoweb.


### Optimizing Images

You can optimize your original images in place and strip their metadata, which
is recommended if you are going to host the files on a server:

> photoweb -o .

By default, this uses a [perceptual algorithm](https://en.wikipedia.org/wiki/Structural_similarity)
to find the best quality setting for each image. This can be slow; to optimize 
more quickly without perceptual search:

> photoweb -o -f .

Optimization will also strip all metadata from the images for privacy and 
file size reduction.


## Creating and Using Templates

By default, the bundled default template will be used. You can edit this, or
create new templates, using them with the -t option:

> photoweb -t "my template" .

To bootstrap your own template, you can copy the default one:

> photoweb --copy-templates ./my-custom-design

Templates are directories with the following files in them:

* md.json - a configuration file
* gallery.html - the overview page
* detail.html - a single photo page
* style.css - visual styling
* photoweb.js - interactive logic (for keyboard navigation and zoom)

Take a look at the default template to get an idea of how to create your own.


## Navigation and Shortcuts

When viewing a photo in the generated gallery:
* **Left/Right Arrow keys**: Previous/Next photo.
* **Escape**: Return to the gallery index.
* **Click/Tap**: Toggle between fit-to-screen and full-size view.
