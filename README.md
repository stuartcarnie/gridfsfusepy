gridfsfusepy
============
A FUSE filesystem for GridFS written in Python using the excellent [fusepy](https://github.com/terencehonles/fusepy) 
bindings.

Features
--------

* Read/only, though read/write is planned next
* Folder support
  * gridfsfusepy will parse out the `filename` property, to create a directory structure by splitting forward slashes (`/`) 
    into subdirectories

Dependencies
------------
The following components must be installed prior to using gridfsfusepy

* [FUSE for OSX](http://osxfuse.github.com/) or compatible library
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
gridfsfusepy and fusepy has been tested with [FUSE for OSX](http://osxfuse.github.com/) on Mountain Lion 10.8

