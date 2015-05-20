from translate.storage import base
from l20nparser import L20nParser

class l20nunit(base.TranslationUnit):
    """Single L20n Entity"""

    def __init__(self, source=''):
        super(l20nunit, self).__init__(source)
        self.id = ''
        self.value = ''
        self.attrs = []
        self.value_index = None
        self.source = source
        pass

    def getsource(self):
        return self.id

    def setsource(self, source):
        self.id = source

    source = property(getsource, setsource)

    def gettarget(self):
        return self.value

    def settarget(self, target):
        self.value = target

    target = property(gettarget, settarget)

    def getid(self):
        return self.id

    def setid(self, new_id):
        self.id = new_id

    def getoutput(self):
        if self.value_index:
            values = []
            for k in ['zero', 'one', 'two', 'few', 'many', 'other']:
                if k in self.value:
                    values.append("  %s: '%s'" % (k, self.value[k]))

            return '''<%(key)s[@cldr.plural($%(extra)s)] {\n%(values)s\n}>''' % {
                'values': "\n".join(values),
                'extra': self.value_index[1],
                'key': self.id
            }
        return '''<%(key)s "%(value)s">''' % {
            'value': self.value,
            'key': self.id
        }

class l20nfile(base.TranslationStore):
    UnitClass = l20nunit

    def __init__(self, inputfile=None):
        super(l20nfile, self).__init__(unitclass=self.UnitClass)
        self.filename = getattr(inputfile, 'name', '')
        if inputfile is not None:
            l20nsrc = inputfile.read()
            self.parse(l20nsrc)
            self.makeindex()

    def parse(self, l20nsrc):
        parser = L20nParser()
        ast = parser.parse(l20nsrc)

        for entry in ast:
            newl20n = l20nunit()
            newl20n.id = entry['$i']
            newl20n.value = entry['$v']

            if '$x' in entry:
                newl20n.value_index = [{
                    'type': 'idOrVal',
                    'value': 'plural'
                }, entry['$x'][1]]
            self.units.append(newl20n)

            for key in entry.keys():
                if key[0] != '$':
                    self.add_attr(newl20n, key, entry[key])

    def add_attr(self, unit, id, attr):
        unit.attrs.append({'id': id, 'value': attr})

    def __str__(self):
        lines = []
        for unit in self.units:
            lines.append(unit.getoutput())
        uret = u"\n".join(lines)
        return uret
