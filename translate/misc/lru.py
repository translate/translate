#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of translate.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

#!/usr/bin/env python

from collections import deque
from weakref import WeakValueDictionary
import gc

class LRUCachingDict(WeakValueDictionary):
    """Caching dictionary like object that discards the least recently
    used objects when number of cached items exceeds maxsize.

    cullsize is the fraction of items that will be discarded when
    maxsize is reached.
    """
    
    def __init__(self, maxsize, cullsize=2, *args, **kwargs):
        self.cullsize = max(2, cullsize)
        self.maxsize = max(cullsize, maxsize)
        self.queue = deque()
        WeakValueDictionary.__init__(self, *args, **kwargs)

                      
    def __setitem__(self, key, value):
        # check boundaries to minimiza duplicate references
        while len(self.queue) and self.queue[0][0] == key:
            # item at left end of queue pop it since it'll be appended
            # to right
            self.queue.popleft()

        while len(self.queue) and self.queue[-1][0] == key:
            # item at right end of queue pop it since it'll be
            # appended again
            self.queue.pop()

        self.queue.append((key, value))
        WeakValueDictionary.__setitem__(self, key, value)

        if len(self) > self.maxsize:
            while len(self) > (self.maxsize - self.maxsize / self.cullsize):
                # maximum cache size exceeded, remove an old item
                self.queue.popleft()
                while gc.collect() > 0:
                    pass


    def __getitem__(self, key):
        value = WeakValueDictionary.__getitem__(self, key)
        # check boundaries to minimiza duplicate references
        while len(self.queue) > 1 and self.queue[0][0] == key:
            # item at left end of queue pop it since it'll be appended
            # to right
            self.queue.popleft()

        # only append if item is not at right end of queu
        if not (len(self.queue) and self.queue[-1][0] == key):
            self.queue.append((key, value))
            
        return value

    def __delitem__(self, key):
        # can't efficiently find item in queue to delete, check
        # boundaries. otherwise just wait till next cache purge
        while len(self.queue) and self.queue[0][0] == key:
            # item at left end of queue pop it since it'll be appended
            # to right
            self.queue.popleft()

        while len(self.queue) and self.queue[-1][0] == key:
            # item at right end of queue pop it since it'll be
            # appended again
            self.queue.pop()
        
        return WeakValueDictionary.__delitem__(self, key)
        

    def clear(self):
        self.queue.clear()
        return WeakValueDictionary.clear(self)


    def setdefault(self, key, default):
        if key not in self:
            self[key]=default
            
        return self[key]
