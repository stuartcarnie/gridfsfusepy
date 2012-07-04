gridfsfusepy
============
A FUSE filesystem for GridFS written in Python using the excellent [fusepy](https://github.com/terencehonles/fusepy) 
bindings.

About
-----
[gridfsfusepy](http://github.com/scarnie/gridfsfusepy) was written by [Stuart Carnie](http://github/scarnie).  

You can find him loitering the internets

* [Blog](http://aussiebloke.blogspot.com)
* [Twitter](http://twitter.com/stuartcarnie)

Features
--------
* Read/only, though read/write is planned next
* Folder support
  * gridfsfusepy will parse out the `filename` property, to create a directory structure by splitting forward slashes (`/`) 
    into subdirectories

Dependencies
------------
The following components must be installed prior to using gridfsfusepy

* [FUSE for OSX](http://osxfuse.github.com/) or [FUES for Linux](http://fuse.sourceforge.net/)
* [fusepy](https://github.com/terencehonles/fusepy) Python bindings for fuse

Usage
-----
    python gridfsfusepy.py mongo_db_name collection_name mount_point
	
### Where:
* `mongo_db_name` is MongoDB database name
* `collection_name` is name of GridGS collection name, e.g. `fs`
* `mount_point` is name of folder to mount GridFS filesystem

Compatibility
-------------

### OS X
gridfsfusepy and fusepy has been tested with [FUSE for OSX](http://osxfuse.github.com/) on Mountain Lion 10.8.

### Linux
There is no reason gridfsfusepy shouldn't work on various Linux distros.  I'll update this space when it is confirmed.

Changelog
---------

**0.1.0**: Initial release

* Read-only support
* Automatic Folder hierarchy, delimiting `filename` by `/`