#! /usr/bin/env python
"""Setup file for distutils

__author__ = "http://www.gemalto.com"

Copyright 2001-2007 gemalto
Author: Jean-Daniel Aussel, mailto:jean-daniel.aussel@gemalto.com

This file is part of pyscard.

pyscard is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 2.1 of the License, or
(at your option) any later version.

pyscard is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with pyscard; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

from distutils import core
from distutils.core import Extension
from distutils.util import get_platform
from distutils.command.build_ext import build_ext
import glob, os, sys

if sys.version[0:1] == '1':
    raise RuntimeError, ("pyscard requires Python 2.x to build.")

print get_platform()
if 'win32'==get_platform():
    platform__cc_defines=[('WIN32', '100')]
    platform_swig_opts=['-DWIN32']
    platform_sources=['smartcard/scard/scard.rc']
    platform_libraries=['winscard']
    platform_include_dirs=[]
    platform_extra_compile_args=[]
    platform_extra_link_args=[]
elif get_platform() in ('linux-i586', 'linux-i686', 'linux-x86_64'):
    platform__cc_defines=[('PCSCLITE', '1')]
    platform_swig_opts=['-DPCSCLITE']
    platform_sources=[]
    platform_libraries=['pcsclite']
    platform_include_dirs=['/usr/include/PCSC']
    platform_extra_compile_args=[]#['-ggdb', '-O0']
    platform_extra_link_args=[]#['-ggdb']
elif get_platform() in ('macosx-10.3-fat', 'darwin-8.9.1-i386', 'darwin-8.10.1-i386', 'macosx-10.5-i386'):
    platform__cc_defines=[('PCSCLITE', '1'),('__APPLE__','1')]
    platform_swig_opts=['-DPCSCLITE', '-D__APPLE__']
    platform_sources=[]
    platform_libraries=[]
    platform_include_dirs=['PCSC']
    platform_extra_compile_args=['-v','-framework', 'PCSC']
    platform_extra_link_args=[]
else:
    sys.exit("unsupported platform: " + get_platform() )


class _pyscardBuildExt(build_ext):
    '''Specialization of build_ext to enable swig_opts'''
if sys.version_info < (2,4):

    # This copy of swig_sources is from Python 2.3.
    # This is to add support of swig_opts for Python 2.3
    # (in particular for MacOS X darwin that comes with Python 2.4)

    def swig_sources (self, sources):

        """Walk the list of source files in 'sources', looking for SWIG
        interface (.i) files.  Run SWIG on all that are found, and
        return a modified 'sources' list with SWIG source files replaced
        by the generated C (or C++) files.
        """

        new_sources = []
        swig_sources = []
        swig_targets = {}

        # XXX this drops generated C/C++ files into the source tree, which
        # is fine for developers who want to distribute the generated
        # source -- but there should be an option to put SWIG output in
        # the temp dir.

        if self.swig_cpp:
            target_ext = '.cpp'
        else:
            target_ext = '.c'

        for source in sources:
            (base, ext) = os.path.splitext(source)
            if ext == ".i":             # SWIG interface file
                new_sources.append(base + target_ext)
                swig_sources.append(source)
                swig_targets[source] = new_sources[-1]
            else:
                new_sources.append(source)

        if not swig_sources:
            return new_sources

        swig = self.find_swig()
        swig_cmd = [swig, "-python"]
        if self.swig_cpp:
            swig_cmd.append("-c++")

        swig_cmd += platform_swig_opts 

        for source in swig_sources:
            target = swig_targets[source]
            self.announce("swigging %s to %s" % (source, target))
            self.spawn(swig_cmd + ["-o", target, source])

        return new_sources
    
    build_ext.swig_sources = swig_sources

kw = {'name':"pyscard",
      'version':"1.6.4",
      'description':"Smartcard module for Python.",
      'author':"Jean-Daniel Aussel",
      'author_email':"aussel.jean-daniel@gemalto.com",
      'url':"http://www.gemalto.com",
      'long_description':'Smartcard package for Python',
      'license':'GNU LESSER GENERAL PUBLIC LICENSE',
      'platforms':['linux','win32'],
      'packages' : [ "smartcard",
                     "smartcard/pcsc",
                     "smartcard/reader",
                     "smartcard/scard",
                     "smartcard/sw",
                     "smartcard/util",
                     "smartcard/wx",
                     ],
      'package_dir' : { "":"." },
      'package_data' : {
                         "smartcard" : [
                                        "ACKS",
                                        "ChangeLog",
                                        "LICENSE",
                                        "README",
                                        "TODO",
                                        ],
                         "smartcard/wx" : ["resources/*.ico"],
                       } ,

      # the _scard.pyd extension to build
      'ext_modules':[Extension("smartcard.scard._scard",
                             define_macros=platform__cc_defines,
                             include_dirs=['smartcard/scard/']+platform_include_dirs,
                             sources=["smartcard/scard/helpers.c",
                                      "smartcard/scard/winscarddll.c",
                                      "smartcard/scard/scard.i"]+platform_sources,
                             libraries=platform_libraries,
                             extra_compile_args=platform_extra_compile_args,
                             extra_link_args=platform_extra_link_args,
                             swig_opts=['-outdir','smartcard/scard']+platform_swig_opts)],
      'cmdclass':{'build_ext': _pyscardBuildExt}
     }

# If we're running >Python 2.3, add extra information
if hasattr(core, 'setup_keywords'):
    if 'classifiers' in core.setup_keywords:
        kw['classifiers'] = [
          'Development Status :: 1.6.4 - Release',
          'License :: GNU LESSER GENERAL PUBLIC LICENSE',
          'Intended Audience :: Developers',
          'Operating System :: Unix',
          'Operating System :: Microsoft :: Windows',
          'Topic :: Security :: Smartcards',
          ]
    if 'download_url' in core.setup_keywords:
        kw['download_url'] = ('http://sourceforge.net/projects/pyscard/'
                              '%s-%s.zip' % (kw['name'], kw['version']) )


core.setup(**kw)






