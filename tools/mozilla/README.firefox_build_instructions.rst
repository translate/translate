================
Firefox Building
================  

The following are instructions for setting up a build environment
to use the Translate Toolkit and Pootle hosted at pootle.locamotion.org
to build Firefox and Firefox Mobile.

There are bound to be issues as we progress but generally the scripts
and tools are widely tested managing over 15 languages.


Setting up your environment
===========================

We use vagrant to manage VirtualBox VMs easily

1. Install VirtualBox
   Downloads https://www.virtualbox.org/wiki/Downloads
   Vagrant installation instructions http://vagrantup.com/v1/docs/getting-started/index.html
2. Install Vagrant
   Downloads http://downloads.vagrantup.com/
3. Create a directory for your Firefox work.  We use ~/dev/mozilla
   # mkdir -p ~/dev/mozilla
   # cd ~/dev/mozilla
4. # wget https://raw.github.com/translate/translate/master/tools/mozilla/Vagrantfile
5. # vagrant up
6. # vagrant ssh
7. # sudo ./postinstall.sh
8. # exit
9. # vagrant halt
10. # vagrant up
11. # vagrant ssh
12. # ./setup_mozilla.sh

You now have a VM that we will use exclusively for Firefox localisation.


Configuring your development setup
==================================

We need to setup some things so that you can work with
version control and have access to the servers.

1. Setup SSH for access to Mozilla mercurial
   Your SSH setup is copied from your computer into vagrant so if
   this already works on your computer then it is already setup.
2. Copy ~/.hgrc and ~/.gitconfig into $HOME on vagrant
3. Send your public key for access to the Pootle server (usually ~/.ssh/id_dsa.pub)
4. Request commit access to the SourceForge ZAF project to store your PO files

Now you should be able to commit changes in PO and Mozilla files. You should
also be able to get and push translations to the Pootle server.


Building Firefox
================

The previous steps are once off.  You have a build setup and access to version control.
The following are steps that you will repeat for every build.
In the following examples we are working with the fictitious language zz.  Replace zz
with your language code.

1. Get ready.
   # vagrant ssh
   # cd firefox
2. Get the new PO translations from Pootle.
   # cd po
   # svn up zz
   # ./get-from-pootle.sh zz
3. Review and commit translations.
   # svndiff zz
   Review the diff and check for any glaring errors.  If you 
   are happy then commit.  We commit before we work on the files so that we
   have something to go back to. Please use a good message as this is used by
   others to track the changes.  E.g. could be.  "Update to 100% in user1 for Zedzed",
   "Update translations following Zedzed sprint"
   # svn ci zz
   Files are now committed and we can get ready to process.
4. Begin updateing. You might want to tell your team that you are doing this
   as any changes they make on Pootle will be lost at a later step.
   # cd ~/firefox
   # ./build_firefox.sh zz
   A lot of processing will happen and it will take some time.  Check for any errors in the process.
5. Now check the updated PO files
   # cd po-updated
   # svndiff zz
   Review for any glaring errors.  You probably only care about such updates after
   a large migration e.g. Aurora 12 to Aurora 13.  If you are still in the same Aurora cycle then
   you don't really care about po-updated output.  Happy? Then commit as you did in po/
   Find any errors?  Fix them on Pootle or in the files in po/zz and run build_firefox.sh
   again.
6. Now we push our work to Mozilla
   # cd ~/firefox/l10n
   Check that Axel's compare locales pass
   # ./compare-locales.sh zz
   Check for any errors and correct.  Removed files should be fixed here. Errors in 
   translations should be fixed on Pootle or in po/
   # cd zz
   # hg status
   Check for any new or removed files. ? means a file not in version control.  ! means a files
   that was in version control and now isn't which usually means we don't need it anymore.
   # hg addremove path/to/files.dtd
   Add the files and please carefully check what you are adding.  You shouldn't be adding anything
   ending in .orig
   # hg diff
   Review the changes and check that you haven't broken anything. Happy?
   # hg commit
   # hg push
   If your push fails with remote: 'ssl required' then you need to do the following.  Edit
   l10/zz/.hg/hgrc, duplicate the line 'default = http:....' and replace default with default-push,
   replace http:// with ssh://
   Now try push again.
7. Wait for Mozilla to build your stuff
   Go to https://l10n-stage-sj.mozilla.org/teams/zz (Change zz of course) and check
   that you have been built.
   Get your nightly test build from
   http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-mozilla-aurora/
   Once you have tested.  Signoff your build at the URL above.
8. Push changes back to Pootle
   If you made committed changes in po-updated/zz then:
   # cd ~/firefox/po
   # cd zz
   # svn up
   Or commit any changes you made in po/zz
   # svn ci
   Please please tell us what the commit is about
   Now you need to push the files to Pootle
   # ./push-to-pootle.sh zz
   You will be asked if you want to proceed.  This is just a check that first syncs files on
   Pootle to check that nobody has made any changes.  Remember your files will overwrite
   anything done in your language on Pootle.
   Happy? Press y<enter>
   You are now synced and can tell your team to continue translating.


Handling types of errors
========================

* The best place to fix anything is on Pootle.  So try to do it there if possible.
* If you need to do it on the PO files, make sure you get-from-pootle.sh before you work
  and push-to-pootle.sh after your changes.  When pushing check that nobody has done any
  work while you were busy, do that by checking the last activity column at
  http://mozilla.locamotion.org/projects/firefox/
* compare-locale fixes are best done with the files in po/zz for speed.  Fix them all before
  doing another build
* If you see Mozilla bugs against your language:  Fix them in Pootle, then close the bug.  Your fix
  will come through in your next update.  If it is urgent you probably want to fix it in PO and
  make sure you push it through to Mozilla.
* If you see your translators making a common error please share it on the firefox-l10n
  list and try to educate them.


build_firefox.sh options
------------------------

--no-vc - No version control.  Won't update anything from Mozilla.  This is helpful if you are working on
          e.g. Aurora 12 and we haven't moved to Aurora 13.  Nothing should change in the source 
          text.  This options will shave off a lot of time.  If uncertain leave this off.
--xpi - Build a language pack.  If you aren't in Mozilla this is the only way to build one.  If your
        language is in Mozilla Mercurial, best to let Mozilla build your langpack.


Notes
=====
As long as you commit before major work you will be able to rollback any major issue.
So be brave and careful.
