gridfsfusepy
============
A FUSE filesystem for GridFS written in Python using the excellent [fusepy](https://github.com/terencehonles/fusepy) 
bindings.

Features
--------

* Read Only
* Folder support
  * gridfsfusepy will parse out the `filename` property, to create a directory structure by splitting forward slashes (`/`) 
    into subdirectories

Dependencies
------------
* [FUSE for OSX](http://osxfuse.github.com/) or compatible library
* [fusepy](https://github.com/terencehonles/fusepy) Python bindings for fuse

Compatibility
-------------
gridfsfusepy and fusepy has been tested with [FUSE for OSX](http://osxfuse.github.com/) on Mountain Lion 10.8
