# -*- coding: utf-8 -*-

"""Convert flat XML files to Gettext PO localization files.

TODO: examples/usage
"""

from translate.convert import convert
from translate.storage import flatxml, po


class flatxml2po(object):
    """Convert a single XML file to a single PO file."""

    SourceStoreClass = flatxml.FlatXMLFile
    TargetStoreClass = po.pofile
    TargetUnitClass = po.pounit

    def __init__(self, inputfile, outputfile, templatefile=None,
                 root="root", value="str", key="key", ns=None):
        """Initialize the converter."""
        self.inputfile = inputfile
        self.outputfile = outputfile

        self.source_store = self.SourceStoreClass(inputfile,
                                                  root_name=root,
                                                  value_name=value,
                                                  key_name=key,
                                                  namespace=ns)
        self.target_store = self.TargetStoreClass()

    def convert_unit(self, unit):
        """Convert a source format unit to a target format unit."""
        target_unit = self.TargetUnitClass.buildfromunit(unit)
        return target_unit

    def convert_store(self):
        """Convert a single source file to a target format file."""
        for source_unit in self.source_store.units:
            self.target_store.addunit(self.convert_unit(source_unit))

    def run(self):
        """Run the converter."""
        self.convert_store()

        if self.target_store.isempty():
            return 0

        self.target_store.serialize(self.outputfile)
        return 1


def run_converter(inputfile, outputfile, templatefile=None,
                  root="root", value="str", key="key", ns=None):
    """Wrapper around the converter."""
    return flatxml2po(inputfile, outputfile, templatefile,
                      root, value, key, ns).run()


formats = {
    "xml": ("po", run_converter),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(formats,
                                         description=__doc__)

    parser.add_option("-r", "--root", action="store", dest="root",
                      default="root",
                      help='name of the XML root element (default: "root")')
    parser.add_option("-v", "--value", action="store", dest="value",
                      default="str",
                      help='name of the XML value element (default: "str")')
    parser.add_option("-k", "--key", action="store", dest="key",
                      default="key",
                      help='name of the XML key attribute (default: "key")')
    parser.add_option("-n", "--namespace", action="store", dest="ns",
                      default=None,
                      help="XML namespace uri (default: None)")

    parser.passthrough.append("root")
    parser.passthrough.append("value")
    parser.passthrough.append("key")
    parser.passthrough.append("ns")

    parser.run(argv)


if __name__ == "__main__":
    main()
