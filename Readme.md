khronos-man-page-mirror
=======================

(original author: Matthäus G. Chajdas)

This project consists of a script to create an (offline) mirror of the Khronos OpenGL manual pages. It also provides a new, jQuery based index which allows for quick search and has better usability than the original, nested index.

## License

All of this is provided under the BSD license. See the `COPYING` file for details.

## Requirements

The bootstrap script expects to be run in a Linux environment. It may work on Mac OS X and Cygwin, but it hasn't been tested. On Ubuntu, the ``lxml`` installation requires a few packages to be installed first. You can get them using ``apt-get install libxml2-dev libxslt1-dev python-dev``.

Both the bootstrapper as well as the final generator requires Python 3.4. It may work with previous versions, but it hasn't been tested. The offline viewer requires only Python 3, and should work on any operating system.

## Running

First, grab all the dependencies by running the bootstrap script. It will download the man pages from the Khronos SVN, which can take several minutes.

Once you have all the data, simply run ``makeindex.py`` to generate the man page package. The output will be placed in the ``build`` subdirectory.

### Offline package

The offline package is built in ``build/offline``. It consists of two ``zip`` files, one containing a copy of MathJax and the other containing the man pages. Use the provided document server (``nDocSrv``) to view them. The ``nDocSrv`` expects the name of the man page archive as the first argument, for example, ``nDocSrv.py gl-4.0.zip``. Alternatively, you can extract the two ``zip`` files and serve them using a standard HTTP server.
