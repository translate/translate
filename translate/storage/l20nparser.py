import re

class ParserError(Exception):
    def __init__(self, message, pos, context):
        self.name = 'ParserError'
        self.message = message
        self.pos = pos
        self.context = context

class L20nParser():
    def __init__(self):
        self._patterns = {
            'identifier': re.compile(r'[A-Za-z_]\w*'),
            'controlChars': re.compile(r'\\([\\\"\'{}])'),
            'unicode': re.compile(r'\\u[0-9a-fA-F]{1,4}'),
            'index': re.compile(r'@cldr\.plural\(\$?(\w+)\)'),
            'placeables': re.compile(r'\{\{\s*([^\s]*?)\s*\}\}'),
        }

    def parse(self, string):
        self._source = string
        self._index = 0
        self._length = len(string)

        return self.getL20n()

    def getAttributes(self):
        attrs = {}

        while True:
            attr = self.getKVPWithIndex()
            attrs[attr[0]] = attr[1]
            ws1 = self.getRequiredWS()
            ch = self._source[self._index]
            if ch == '>':
                break
            elif not ws1:
                raise self.error('Expected ">"')
        return attrs

    def getKVP(self):
        key = self.getIdentifier()
        self.getWS()
        if self._source[self._index] != ':':
            raise self.error('Expected ":"')
        self._index += 1
        self.getWS()
        return [key, self.getValue()]

    def getKVPWithIndex(self, type=None):
        key = self.getIdentifier()
        index = []

        if self._source[self._index] == '[':
            self._index += 1
            self.getWS()
            index = self.getIndex()
        self.getWS()
        if self._source[self._index] != ':':
            raise self.error('Expected ":"')
        self._index += 1
        self.getWS()
        return [key, self.getValue(False, None, index)]

    def getHash(self):
        self._index += 1
        self.getWS()
        hi = None
        comma = None
        hash = {}

        while True:
            hi = self.getKVP()
            hash[hi[0]] = hi[1]
            self.getWS()

            comma = self._source[self._index] == ','

            if comma:
                self._index += 1
                self.getWS()

            if self._source[self._index] == '}':
                self._index += 1
                break
            if not comma:
                raise self.error('Expected "}"')

        return hash

    def unescapeString(self, str):
        str = re.sub(self._patterns['controlChars'], lambda m: m.group(1), str)

        # only supports \uXXXX, not \uXXX or shorter
        return str.decode('unicode-escape')

    def getString(self, opchar):
        opchar_pos = self._source.find(opchar, self._index + 1)

        while opchar_pos != -1 and \
            ord(self._source[opchar_pos - 1]) == 92 and \
            ord(self._source[opchar_pos - 2]) != 92:
            opchar_pos = self._source.find(opchar, opchar_pos + 1)

        if opchar_pos == -1:
            raise self.error('Unclosed string literal')

        buf = self._source[self._index + 1: opchar_pos]

        self._index = opchar_pos + 1

        # bug in js code?
        if buf.find('\\') != -1:
            buf = self.unescapeString(buf)

        if buf.find('{{') != -1:
            return self.parseString(buf)
        return buf

    def getValue(self, optional=False, ch=None, index=None):
        if ch is None:
            if self._length > self._index:
                ch = self._source[self._index]
            else:
                ch = None
        if ch == "'" or ch == '"':
            val = self.getString(ch)
        if ch == '{':
            val = self.getHash()

        if val is None:
            if not optional:
                raise self.error('Unknown value type')
            return None

        if index:
            return {
                '$v': val,
                '$x': index
            }
        return val

    def getRequiredWS(self):
        pos = self._index
        cc = ord(self._source[self._index])

        while cc == 32 or cc == 10 or cc == 9 or cc == 13:
            self._index += 1
            if self._length <= self._index:
                break
            cc = ord(self._source[self._index])
        return pos != self._index

    def getWS(self):
        cc = ord(self._source[self._index])

        while cc == 32 or cc == 10 or cc == 9 or cc == 13:
            self._index += 1
            if self._length <= self._index:
                break
            cc = ord(self._source[self._index])

    def getIdentifier(self):
        reId = self._patterns['identifier']

        match = reId.match(self._source[self._index:])

        self._index += match.end()
        return match.group(0)


    def getEntity(self, id, index):
        entity = {'$i': id}

        if index:
            entity['$x'] = index

        if not self.getRequiredWS():
            raise self.error('Expected white space')

        ch = self._source[self._index]
        value = self.getValue(index is None, ch)
        attrs = None

        if value is None:
            if ch == '>':
                raise self.error('Expected ">"')
            attrs = self.getAttributes()
        else:
            entity['$v'] = value
            ws1 = self.getRequiredWS()
            if not self._source[self._index] == '>':
                if not ws1:
                    raise self.error('Expected ">"')
                attrs = self.getAttributes()

        self._index += 1
        if attrs:
            for key in attrs:
                entity[key] = attrs[key]

        return entity

    def getEntry(self):
        # 66 === '<'
        if ord(self._source[self._index]) == 60:
            self._index += 1
            id = self.getIdentifier()
            # 91 === '['
            if ord(self._source[self._index]) == 91:
                self._index += 1
                return self.getEntity(id, self.getIndex())
            return self.getEntity(id, None)
        raise self.error('Invalid entry')

    def getL20n(self):
        ast = []

        self.getWS()

        while self._index < self._length:
            ast.append(self.getEntry())
            if self._index < self._length:
                self.getWS()
        return ast

    def getIndex(self):
        self.getWS()
        match = self._patterns['index'].match(self._source[self._index:])
        self._index += len(match.group(0))
        self.getWS()
        self._index += 1
        return [{'t': 'idOrVar', 'v': 'plural'}, match.group(1)]

    def parseString(self, str):
        return str

    def error(self, message, pos=None):
        if pos is None:
            pos = self._index
        start = self._source.rfind('<', pos - 1)
        lastClose = self._source.rfind('>', pos - 1)
        start = lastClose + 1 if lastClose > start else start
        context = self._source[start:pos + 10]

        msg = '%s at pos %s: "%s"' % (message, pos, context)
        return ParserError(msg, pos, context)
