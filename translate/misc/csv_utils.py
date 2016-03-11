import csv
import six


class UnicodeDictWriter(csv.DictWriter):
    """Utility class to allow writing csv from unicode content on Python 2.
    Might probably be dropped once Python 2 support will cease.
    """

    def __init__(self, f, fieldnames, encoding='utf-8', **kwargs):
        csv.DictWriter.__init__(self, f, fieldnames, **kwargs)
        self.encoding = encoding

    def encode(self, value):
        if six.PY2:
            return value.encode(self.encoding)
        return value

    def writerow(self, rowdict):
        self.writer.writerow([self.encode(item) for item in self._dict_to_list(rowdict)])
