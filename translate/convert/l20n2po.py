#!/usr/bin/env python

"""Convert Mozilla .l20n files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/l20n2po.html
for examples and usage instructions.
"""

from translate.storage import po, l20n

class l20n2po:
    """convert a .l20n file to a .po file for handling the
    translation."""

    def __init__(self, blankmsgstr=False, duplicatestyle="msgctxt"):
        pass

    def convertl20nunit(self, store, unit):
        po_units = []

        po_unit = po.pounit(encoding="UTF-8")
        po_unit.addlocation(unit.getid())
        po_unit.setid(unit.getid())
        if unit.value_index:
            # the value here may be a string or a hash
            # if it's a hash it will look like this:
            #
            # unit.value_index - [{'type': 'idOrVal', 'value': 'plural'}, 'n']
            # unit.value - {'one': 'value', 'many': 'value2'}
            #
            # I don't know how to turn it into a plural po entity
            if unit.value_index[0]['value'] == 'plural':
                po_unit.source = unit.value['one']
            pass
        else:
            po_unit.source = unit.value
        po_units.append(po_unit)

        for attr in unit.attrs:
            po_unit = po.pounit(encoding="UTF-8")

            id = '%s.%s' % (unit.getid(), attr['id'])
            po_unit.addlocation(id)
            po_unit.setid(id)
            po_unit.source = attr['value']
            po_units.append(po_unit)
        return po_units

    def convertstore(self, l20n_store):
        """converts a .l20n file to a .po file..."""
        target_store = po.pofile()
        targetheader = target_store.header()
        targetheader.addnote("extracted from %s" % l20n_store.filename,
                             "developer")
        l20n_store.makeindex()
        for l20nunit in l20n_store.units:
            pounits = self.convertl20nunit(l20n_store, l20nunit)
            for pounit in pounits:
                target_store.addunit(pounit)
        return target_store

    def mergestore(self, origl20nfile, translatedl20nfile):
        """converts two .l20n files to a .po file..."""
        target_store = po.pofile()
        targetheader = target_store.header()
        targetheader.addnote("extracted from %s, %s" % (origl20nfile.filename,
                                                        translatedl20nfile.filename),
                             "developer")
        origl20nfile.makeindex()
        for l20nunit in origl20nfile.units:
            pounits = self.convertl20nunit(origl20nfile, l20nunit)
            for pounit in pounits:
                target_store.addunit(pounit)
                if pounit.getid() in translatedl20nfile.locationindex:
                    print('fooo')
                    print(pounit.name)
        return target_store
        

def convertl20n(inputfile, outputfile, templatefile,
                pot=False, duplicatestyle="msgctxt"):
    inputstore = l20n.l20nfile(inputfile)
    convertor = l20n2po(blankmsgstr=pot,
                        duplicatestyle=duplicatestyle)
    if templatefile is None:
        outputstore = convertor.convertstore(inputstore)
    else:
        templatestore = l20n.l20nfile(templatefile)
        outputstore = convertor.mergestore(templatestore, inputstore)
    if outputstore.isempty():
        return 0
    outputfile.write(str(outputstore))
    return 1

formats = {
    "l20n": ("po", convertl20n),
    ("l20n", "l20n"): ("po", convertl20n),
}

def main(argv=None):
    from translate.convert import convert

    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         usepots=True, description=__doc__)
    parser.add_duplicates_option()
    parser.passthrough.append("pot")
    parser.run(argv)


if __name__ == '__main__':
    main()
