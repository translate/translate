Reporting Bugs
==============

If you have problems with some tool, ensure that you have the newest version of the tool you are using. Check the documentation of the tool to see if the examples or other guidelines can help. If you are lucky, your problem is not a bug at all.

If you feel you found a bug, please make sure you are aware of the bug etiquette explained below. Then report your bugs at https://github.com/translate/translate/issues.

Bug Etiquette
-------------

In order to best solve the problem we need good bug reports.  Reports that do not give a full picture or which coders are unable to 
reproduce, end up wasting a lot of time.  If you, the expert in your bug, spend a bit of time you can make sure your bug gets fixed. 

Remember to first see if the bug is not already reported. Perhaps someone already reported it and you can provide some extra information in that bug report. You can also add yourself in the CC field so that you get notified of any changes to the bug report.

If you could not find the bug, you should report it. Look through each of the following sections and make sure you have given the information required.

Be verbose
----------

Tell us exactly how came to see this bug.  Don't say:

   The Mozilla DTD files have escaping errors

Rather say:

   I'm working on Firefox 1.5 and in the files somefile.dtd entity XXXX the \n is not escaped correctly it should be \\n

OK so we need to know:

- What you where working on
- What tool you used
- What file has an error
- What you got, and
- What you expected to get

Tell us your version
--------------------

Use --version to get the version of the tool you are working with.

.. code-block:: shell

  moz2po --version        # for Translate Toolkit

We might have fixed this problem already, your version will help us know if their are still problems or whether to ask you to upgrade.

Attach examples
---------------

If possible, create a snippet of a file to demonstrate the error.  Sending one large file means that the coder
has to search for the error.  If you can narrow it down to one key section and only attach that, it will help.

Please attach all your source files.  In other words, if the error is in somefile.dtd in Firefox 1.1 please attach that file.  It will save the coder
having to find the Firefox version, extract the file and check.  If the file is included, everything is much quicker.  If the file is very large,
then please place it on a server somewhere for the coder to download.



Include tracebacks
------------------

For the programs in the translate toolkit, use the parameter --errorlevel=traceback and copy the traceback to the bug report

  moz2po --errorlevel=traceback

A traceback will give a much better clue as to what the error might be and send the coder on the right path.  It may be a very simple fix, may relate to your setup or might indicate a much more complex problem.  Tracebacks help coders get you information quicker.

Reproduce
---------

Tell us exactly how to reproduce the error.  Mention the steps if needed, or give an example command line.  Without being able to reproduce the error, it will not easily get fixed.
