#!/usr/bin/env python
#
# Copyright (c) 2009 Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.
#
# Make a release from a tag and push to sf.net
#
# File taken from solarbeam.sf.net project tools

import os
import subprocess
import sys
import shutil
import tempfile

UNIXTITLE = "qontexte"
SF_USER = "numerodix"


def invoke(cwd, args):
    print(">>>>> Running %s :: %s" % (cwd, " ".join(args)))
    popen = subprocess.Popen(args, cwd=cwd,
                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out, _err) = popen.communicate()
    out = str(out).strip()
    return popen.returncode, out

def git_clone(path, newpath):
    args = ["git", "clone", path]
    (code, out) = invoke(newpath, args)
    print(out)
    if code > 0: sys.exit(1)

def git_checkout(path, commit):
    args = ["git", "checkout", commit]
    (code, out) = invoke(path, args)
    print(out)
    if code > 0: sys.exit(1)

def make_zip(path, commit):
    args = ["tools/pkg.sh", commit]
    (code, out) = invoke(path, args)
    print(out)
    if code > 0: sys.exit(1)

def push_to_sf(file, commit):
    args = ["rsync", "-avP", "-e", "ssh",
            "%s" % file, 
            "%s,%s@frs.sourceforge.net:/home/frs/project/%s/%s/%s/%s/" % 
            (SF_USER, UNIXTITLE, UNIXTITLE[0], UNIXTITLE[:2], UNIXTITLE, commit)]
    (code, out) = invoke(os.getcwd(), args)
    print(out)
    if code > 0: sys.exit(1)

def make(commit):
    td = tempfile.mkdtemp(prefix=".%spkg" % UNIXTITLE)

    git_clone(os.getcwd(), td)
    gitpath = os.path.join(td, UNIXTITLE)
    git_checkout(gitpath, commit)

    make_zip(gitpath, commit)
    try:
        os.makedirs(os.path.join(os.getcwd(), "dist"))
    except:
        pass
    archive = "%s-%s.tar.gz" % (UNIXTITLE, commit)
    os.rename(os.path.join(gitpath, archive),
              os.path.join(os.getcwd(), archive))

    shutil.rmtree(td)

    return archive

def printhelp(full=False):
    ss = []
    if full:
        ss.append("Usage:  %s <tag name>\n" % sys.argv[0])
        ss.append("Tag commit:")
        ss.append(" * run scripts/tag.py\n")
        ss.append("Working order:")
        ss.append(" * clone git repo in /tmp")
        ss.append(" * checkout selected tag name")
        ss.append(" * make zip")
        ss.append(" * push to sf.net")
    ss.append("\nManual steps:")
    ss.append(" * update web/releases")
    ss.append(" * run scripts/genreleasepage.py")
    ss.append(" * make webup")
    s = '\n'.join(ss)
    print(s)


if __name__ == "__main__":
    try:
        version = sys.argv[1]
    except IndexError:
        printhelp(full=True)
        sys.exit()

    file = make(version)
    push_to_sf(file, version)
    printhelp()
