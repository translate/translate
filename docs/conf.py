# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys


sys.path.insert(0, os.path.abspath("_ext"))
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "Translate Toolkit"
copyright = "2002-2023, Translate"

# The short X.Y version.
version = "3.8.5"

# The full version, including alpha/beta/rc tags
release = version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "translate_docs",
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "_themes/README.rst", "releases/README.rst"]

# The master toctree document.
master_doc = "index"

# -- Missing modules --------------------------------------------------

autodoc_mock_imports = [
    "aeidon",
    "BeautifulSoup",
    "glib",
    "gobject",
    "gtk",
    "iniparse",
    "vobject",
]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx-bootstrap"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "nosidebar": True,
}

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = ["_themes"]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Output file base name for HTML help builder.
htmlhelp_basename = "TranslateToolkitdoc"


# -- Options for LaTeX output -------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual])
latex_documents = [
    (
        "index",
        "TranslateToolkit.tex",
        "Translate Toolkit Documentation",
        "Translate.org.za",
        "manual",
    ),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output -------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (
        "index",
        "translatetoolkit",
        "Translate Toolkit Documentation",
        ["Translate.org.za"],
        1,
    )
]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output -----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        "TranslateToolkit",
        "Translate Toolkit Documentation",
        "Translate.org.za",
        "TranslateToolkit",
        "One line description of project.",
        "Miscellaneous",
    ),
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'


# -- Coverage checker options -------------------------------------------------

coverage_ignore_modules = []

coverage_ignore_functions = ["main"]

coverage_ignore_classes = []

coverage_write_headline = False

# -- Options for intersphinx extension ---------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "pytest": ("https://docs.pytest.org/en/latest/", None),
    "django": (
        "https://docs.djangoproject.com/en/stable/",
        "https://docs.djangoproject.com/en/stable/_objects/",
    ),
    "pootle": ("https://docs.translatehouse.org/projects/pootle/en/latest/", None),
    "guide": (
        "https://docs.translatehouse.org/projects/localization-guide/en/latest/",
        None,
    ),
}


# -- Options for Exernal links -------------------------------------------------

extlinks = {
    # :role: (URL, prefix)
    "issue": ("https://github.com/translate/translate/issues/%s", "issue %s"),
    "man": ("https://linux.die.net/man/1/%s", "%s"),
    "wp": ("https://en.wikipedia.org/wiki/%s", "%s"),
}

# -- Options for Linkcheck -------------------------------------------------

# Add regex's here for links that should be ignored.
linkcheck_ignore = [
    "http://your_server.com/filename.html",  # Example URL
    ".*localhost.*",
]
