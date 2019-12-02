# -*- coding: utf-8 -*-
#
# archmage -- CHM decompressor
# Copyright (c) 2003 Eugeny Korekin <aaaz@users.sourceforge.net>
# Copyright (c) 2005-2009 Basil Shubin <bashu@users.sourceforge.net>
# Copyright (c) 2015 Mikhail Gusarov <dottedmag@dottedmag.net>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301, USA.
#

"""arCHMage -- extensible reader and decompiler for files in the CHM format.

Usage: %(program)s [options] <chmfile> [destdir|destfile]
Where:

    -x / --extract
        Extracts CHM file into specified directory. If destination
        directory is omitted, than the new one will be created based
        on name of CHM file. This options is by default.

    -c format
    --convert=format
        Convert CHM file into specified file format. If destination
        file is omitted, than the new one will be created based
        on name of CHM file. Available formats:

            html - Single HTML file
            text - Plain Text file
            pdf - Adobe PDF file format

    -d / --dump
        Dump HTML data from CHM file into standard output.

    -V / --version
        Print version number and exit.

    -h / --help
        Print this text and exit.
"""

import os, sys
import getopt

import archmage
from archmage.CHM import CHMFile

# Return codes
OK = 0
ERROR = 1

program = sys.argv[0]

# Miscellaneous auxiliary functions
def message(code=OK, msg=''):
    outfp = sys.stdout
    if code == ERROR:
        outfp = sys.stderr
    if msg:
        print(msg, file=outfp)

def usage(code=OK, msg=''):
    """Show application usage and quit"""
    message(code, __doc__ % globals())
    message(code, msg)
    sys.exit(code)

def parseargs():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'xc:dp:Vh',
                                ['extract', 'convert=', 'dump', 'port=', 'version', 'help'])
    except getopt.error as msg:
        usage(ERROR, msg)

    class Options:
        mode = None        # EXTRACT or other
        chmfile = None     # CHM File to view/extract
        output = None      # Output file or directory

    options = Options()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-V', '--version'):
            message(OK, archmage.__version__)
            sys.exit(OK)
        elif opt in ('-c', '--convert'):
            if options.mode is not None:
                sys.exit('-x and -c are mutually exclusive')
            options.mode = archmage.output_format(str(arg))
        elif opt in ('-x', '--extract'):
            if options.mode is not None:
                sys.exit('-x and -c are mutually exclusive')
            options.mode = archmage.EXTRACT
        elif opt in ('-d', '--dump'):
            if options.mode is not None:
                sys.exit('-d should be used without any other options')
            options.mode = archmage.DUMPHTML
        else:
            assert False, (opt, arg)

    # Sanity checks
    if options.mode is None:
        # Set default option
        options.mode = archmage.EXTRACT

    if not args:
        sys.exit('No CHM file was specified!')
    else:
        # Get CHM file name from command line
        options.chmfile = args.pop(0)

    # if CHM content should be extracted
    if options.mode == archmage.EXTRACT:
        if not args:
            options.output = archmage.file2dir(options.chmfile)
        else:
            # get output directory from command line
            options.output = args.pop(0)
    # or converted into another file format
    elif options.mode in (archmage.CHM2TXT, archmage.CHM2HTML, archmage.CHM2PDF):
        if not args:
            options.output = archmage.output_file(options.chmfile, options.mode)
        else:
            # get output filename from command line
            options.output = args.pop(0)

    # Any other arguments are invalid
    if args:
        sys.exit('Invalid arguments: ' + ', '.join(args))

    return options


def main():
    options = parseargs()
    if not os.path.exists(options.chmfile):
        sys.exit('No such file: %s' % options.chmfile)

    if os.path.isdir(options.chmfile):
        sys.exit('A regular files is expected, got directory: %s' % options.chmfile)

    source = CHMFile(options.chmfile)

    if options.mode == archmage.DUMPHTML:
        source.dump_html()
    elif options.mode == archmage.CHM2TXT:
        if os.path.exists(options.output):
            sys.exit('%s is already exists' % options.output)
        source.chm2text(open(options.output, 'w'))
    elif options.mode in (archmage.CHM2HTML, archmage.CHM2PDF):
        source.htmldoc(options.output, options.mode)
    elif options.mode == archmage.EXTRACT:
        source.extract(options.output)

    source.close()