Making a Translate Toolkit Release
**********************************

This page is divided in three sections. The first one lists the tasks that must
be performed to get a valid package. The second section includes a list of
tasks to get the package published and the release announced. The third one
lists and suggests some possible cleanup tasks to be done after releasing.

.. note:: Please note that this is not a complete list of tasks. Please feel
   free to improve it.


Prepare the relese
==================


Create release notes
--------------------

We create our release notes in reStructured Text, since we use that elsewhere
and since it can be rendered well in some of our key sites.

First we need to create a log of changes in the Translate Toolkit, which is
done generically like this:

.. code-block:: console

    $ git log $(git describe --tags --abbrev=0)..HEAD >> docs/releases/$version.rst


Or a more specific example:

.. code-block:: console

    $ git log $(git describe --tags --abbrev=0)..HEAD > docs/releases/3.6.0.rst


Edit this file.  You can use the commits as a guide to build up the release
notes.  You should remove all log messages before the release.

.. note:: Since the release notes will be used in places that allow linking we
   use links within the notes.  These should link back to products websites
   (`Virtaal <http://virtaal.org>`_, `Pootle
   <http://pootle.translatehouse.org>`_, etc), references to `Translate
   <http://translatehouse.org>`_ and possibly bug numbers, etc.

Read for grammar and spelling errors.

.. note:: When writing the notes please remember:

   #. The voice is active. 'Translate has released a new version of the
      Translate Toolkit', not 'A new version of the Translate Toolkit was
      released by Translate'.
   #. The connection to the users is human not distant.
   #. We speak in familiar terms e.g. "I know you've been waiting for this
      release" instead of formal.

We create a list of contributors using this command:

.. code-block:: console

    $ git log $(git describe --tags --abbrev=0)..HEAD --format='%aN, ' | awk '{arr[$0]++} END{for (i in arr){print arr[i], i;}}' | sort -rn | cut -d\  -f2- >> docs/releases/$version.rst


.. _releasing#up-version-numbers:

Up version numbers
------------------

Update the version number in:

- :file:`translate/__version__.py`
- :file:`docs/conf.py`

In :file:`translate/__version__.py`, bump the build number if anybody used the
Translate Toolkit with the previous number, and there have been any changes to
code touching stats or quality checks.  An increased build number will force a
Translate Toolkit user, like Pootle, to regenerate the stats and checks.

For :file:`docs/conf.py` change ``version`` and ``release``.

.. todo:: FIXME - We might want to consolidate the version and release info so
   that we can update it in one place.


The version string should follow the pattern::

    $MAJOR-$MINOR-$MICRO[-$EXTRA]

E.g. ::

    1.10.0
    0.9.1-rc1 

``$EXTRA`` is optional but all the three others are required.  The first
release of a ``$MINOR`` version will always have a ``$MICRO`` of ``.0``. So
``1.10.0`` and never just ``1.10``.

.. note:: You probably will have to adjust the output of some of the functional
   tests, specifically the manpage ones, to use the right new version.


Publish the new release
=======================

Once the ``master`` branch is ready, the package can be published. This is
automated by :file:`.github/workflows/setup.yml` which automatically publishes
tagged release to PyPI and GitHub.


Tag and branch the release
--------------------------

You should only tag once you are happy with your release as there are some
things that we can't undo. You can safely branch for a ``stable/`` branch
before you tag.

.. code-block:: console

    $ git checkout -b stable/2.2.x
    $ git push origin stable/2.2.x
    $ git tag -a 2.2.5 -m "Tag version 2.2.5"
    $ git push --tags


Release documentation
---------------------

We need a tagged release before we can do this. The docs are published on Read
The Docs.

- https://readthedocs.org/projects/translate-toolkit/versions/

Use the admin pages to flag a version that should be published.

.. note::

    The branches like ``stable/2.2.x`` are automatically enabled on Read the
    Docs using :guilabel:`Automation Rules`, so there might be nothing to do
    here.


Update Translate Toolkit website
--------------------------------

We use github pages for the website. First we need to checkout the pages:

.. code-block:: console

    $ git checkout gh-pages


#. In :file:`_posts/` add a new release posting.  This is in Markdown format
   (for now), so we need to change the release notes .rst to .md, which mostly
   means changing URL links from ```xxx <link>`_`` to ``[xxx](link)``.
#. Change ``$version`` as needed. See :file:`_config.yml` and :command:`git grep $old_release`.
#. :command:`git commit` and :command:`git push` -- changes are quite quick, so
   easy to review.

.. _releasing#create-github-release:

Updating release notes on Github
--------------------------------

#. Open GitHub release created by the GitHub Action.
#. Edit it to include release notes (use same text as used on website).

Announce to the world
---------------------

Let people know that there is a new version:

#. Tweet about the release.

#. Post link to release Tweet to the `Translate gitter channel <https://gitter.im/translate/dev>`_.

#. Update :wp:`Translate Toolkit's Wikipedia page <Translate_Toolkit>`


Post-Releasing Tasks
====================

These are tasks not directly related to the releasing, but that are
nevertheless completely necessary.


Bump version to N+1-alpha1
--------------------------

If this new release is a stable one, bump the version in ``master`` to
``{N+1}-alpha1``. The places to be changed are the same ones listed in
:ref:`Up version numbers <releasing#up-version-numbers>`. This prevents anyone
using ``master`` being confused with a stable release and we can easily check
if they are using ``master`` or ``stable``.

.. note:: You probably will have to adjust the output of some of the functional
   tests, specifically the manpage ones, to use the right new version.


Add release notes for dev
-------------------------

After updating the release notes for the about to be released version, it is
necessary to add new release notes for the next release, tagged as ``dev``.


Other possible steps
--------------------

Some possible cleanup tasks:

- Remove your ``translate-release`` checkout.
- Update and fix these releasing notes:

  - Make sure these releasing notes are updated on ``master``.
  - Discuss any changes that should be made or new things that could be added.
  - Add automation if you can.


We also need to check and document these if needed:

- Change URLs to point to the correct docs: do we want to change URLs to point
  to the ``$version`` docs rather then ``latest``?
- Building on Windows, building for other Linux distros.
- Communicating to upstream packagers.
