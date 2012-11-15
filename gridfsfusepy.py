#!/usr/bin/env python

# gridfsfusepy
#
# Copyright (c) 2012 Stuart Carnie, stuart.carnie@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

__author__ = 'stuartcarnie'
__copyright__ = 'Copyright 2012, Stuart Carnie'
__license__ = 'MIT'
__status__ = 'Development'
__version__ = '0.02.0'

try:
    from fuse import FUSE, FuseOSError, Operations, LoggingMixIn, fuse_get_context
except ImportError as ex:
    print('Failed to import fusepy library; install from github https://github.com/terencehonles/fusepy')
    exit(1)

from stat import S_IFDIR, S_IFREG
from sys import argv
from pymongo import Connection
from errno import *
from gridfs import GridFS
from time import time
import os
from bson.code import Code
from urlparse import urlparse
from pymongo.errors import ConfigurationError

class FuseGridFS(LoggingMixIn, Operations):

    def __init__(self, db_or_uri, collection=None):
        if collection == None:
            url = urlparse(db_or_uri)
            if url.scheme != 'mongodb':
                show_usage()

            path = url.path
            (db_path, collection) = os.path.split(path)
            db = os.path.basename(db_path)

            mongo_uri = ''.join([url[0], '://', url[1], db_path])
        else:
            db = db_or_uri
            mongo_uri = ''

        cn = Connection(mongo_uri)
        self.db = cn[db]
        self.collection = self.db[collection]
        self.gfs = GridFS(self.db, collection=collection)

    def fix_path(self, path):
        if path == '/':
            return ''

        path = path[1:] if path.startswith('/') else path
        path = path.replace('/', '\\/')
        path = path+'\\/' if not path.endswith('/') else path
        return path

    def find_dirs(self, path):
        path = self.fix_path(path)
        map_function = Code('''
        function () {
            var re = /^%s([\w ]+)\//;
            emit(re(this.filename)[1], 1);
        }
        ''' % path)

        reduce_function = Code('''
        function(k,v) {
            return 1;
        }
        ''')
        res = self.collection.files.map_reduce(map_function, reduce_function, out='dirs', query={'filename' : { '$regex' : '^{0}([\w ]+)\/'.format(path) }})
        if res.count() > 0:
            return [a['_id'] for a in res.find()]
        return []

    def find_files(self, path):
        path = self.fix_path(path)
        map_function = Code('''
        function () {
            var re = /^%s([\w ]+(?:\.[\w ]+)*)$/;
            emit(re(this.filename)[1], 1);
        }
        ''' % path)

        reduce_function = Code('''
        function(k,v) {
            return 1;
        }
        ''')
        res = self.collection.files.map_reduce(map_function, reduce_function, out='dirs', query={'filename' : { '$regex' : '^{0}([\w ]+(?:\.[\w ]+)*)$'.format(path) }})
        if res.count() > 0:
            return [a['_id'] for a in res.find()]
        return []

    def is_dir(self, path):
        if path == '/':
            return True

        path = self.fix_path(path)
        res = self.collection.files.find_one({'filename' : { '$regex' : '^{0}'.format(path) }})
        return not res is None

    def readdir(self, path, fh):
        dirs = self.find_dirs(path)
        files = self.find_files(path)

        return ['.', '..'] + dirs + files

    def fuse_to_mongo_path(self, path):
        return path[1:] if path.startswith('/') else path

    def get_mongo_file(self, path):
        path = self.fuse_to_mongo_path(path)
        return self.gfs.get_last_version(filename=path) if self.gfs.exists(filename=path) else None

    def getattr(self, path, fh=None):
        if path == '/' or self.is_dir(path):
            st = dict(st_mode=(S_IFDIR | 0755), st_nlink=2)
        else:
            file = self.get_mongo_file(path)
            if file:
                st = dict(st_mode=(S_IFREG | 0444), st_size=file.length)
            else:
                raise FuseOSError(ENOENT)
        st['st_ctime'] = st['st_mtime'] = st['st_atime'] = time()
        st['st_uid'], st['st_gid'], pid = fuse_get_context()
        return st

    def read(self, path, size, offset, fh):
        file = self.get_mongo_file(path)
        if file:
            file.seek(offset, os.SEEK_SET)
            return file.read(size)
        else:
            raise FuseOSError(ENOENT)

    # Disable unused operations:
    access = None
    flush = None
    getxattr = None
    listxattr = None
    open = None
    opendir = None
    release = None
    releasedir = None
    statfs = None

    def rename_dir(self, old, new):
        print('rename_dir: old=%s, new=%s' % (old, new))

        search = self.fix_path(old)
        res = self.collection.files.find({ 'filename' : { '$regex' : '^{0}'.format(search) } }, fields={ 'filename' : 1 } )
        if not res.count():
            return 0

        new = self.fuse_to_mongo_path(new)
        old = self.fuse_to_mongo_path(old)
        old_len = len(old)

        for a in res:
            new_name = new + a['filename'][old_len:]
            id = a['_id']
            self.collection.files.update({ '_id' : id }, {'$set' : { 'filename' : new_name } })

        return 0

    def rename(self, old, new):
        if self.is_dir(old):
            return self.rename_dir(old, new)

        file = self.get_mongo_file(old)
        if not file:
            raise FuseOSError(ENOENT)

        new = self.fuse_to_mongo_path(new)
        self.collection.files.update({ '_id' : file._id }, {'$set' : { 'filename' : new } })

        return 0


def show_usage():
    print('''
usage: %s [<dbname> <collection>|<mongo_uri>] <mountpoint>

where:
    mongo_uri      mongodb://user:pass@server:port/db/bucket
    ''' % argv[0])
    exit(1)

if __name__ == '__main__':
    argc = len(argv)
    if argc != 3 and argc != 4:
        show_usage()

    try:
        if argc == 4:
            mount_point = argv[3]
            a = FuseGridFS(argv[1], argv[2])
        else:
            mount_point = argv[2]
            a = FuseGridFS(argv[1])

        if os.sys.platform == 'darwin':
            fuse = FUSE(a, mount_point, foreground=True, debug=False, volname='gridfs')
        else:
            fuse = FUSE(a, mount_point, foreground=True, debug=False)

    except ConfigurationError as ex:
        print('ERROR: %s' % ex.message)
        exit(1)
