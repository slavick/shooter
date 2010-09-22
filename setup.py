#! /usr/bin/env python

#
# Copyright (C) 2009 Thadeus Burgess
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

__author__="Thadeus Burgess <thadeusb@thadeusb.com>"
__date__ ="$Mar 21, 2009 12:00:09 AM$"

# Some of this script is from Pete Shinners pygame2exe script.
# Some of this script belongs to GUI2Exe

# import modules
from distutils.core import setup
import py2exe

import sys
import os

import shutil
#from shutil import ignore_patterns

import pygame

pygamedir = os.path.split(pygame.base.__file__)[0]

# Run the script if no commands are supplied
if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    sys.argv.append("-q")

#########################
### Variables to edit ###
#########################

# Stuff to show who made it, etc.
copyright = "Copyright (C) 2009, John Slavick"
author = "John Slavick"
company = ""
# Name of application
name= "Shooter"
# Version
version = "1.0"
# Icon file. Leave blank for the pygame icon.
icon_file = ""

# Starting .py or .pyw script
script = "Shooter.py"
# Final name of .exe file
dest_file = "Shooter"
# Final folder for the files
dest_folder = "dist"
        

data_files = [('res', ['*',]),
              ('sprites', ['*',]),
              ('.', [
                    os.path.join(pygamedir, pygame.font.get_default_font()),
                    os.path.join(pygamedir, 'SDL.dll'),
                    os.path.join(pygamedir, 'SDL_ttf.dll'),
                    os.path.join(pygamedir, 'SDL_image.dll'),
                    os.path.join(pygamedir, 'SDL_mixer.dll'),
                    os.path.join(pygamedir, 'zlib1.dll'),
                    os.path.join(pygamedir, 'jpeg.dll'),
                    os.path.join(pygamedir, 'smpeg.dll'),
                    os.path.join(pygamedir, 'libpng12-0.dll'),
                    os.path.join(pygamedir, 'libfreetype-6.dll'),
                    os.path.join(pygamedir, 'libtiff.dll'),
                    os.path.join(pygamedir, 'libogg-0.dll'),
                    os.path.join(pygamedir, 'libvorbis-0.dll'),
                    os.path.join(pygamedir, 'libvorbisfile-3.dll'),
                    ]
                ),
             ]

packages = ['pygame']
includes = []
excludes = []
dll_excludes = []

if icon_file is '':
    icon_file = '' + os.path.join(pygamedir, 'pygame.ico')

icon_resources = [(1, icon_file)]
bitmap_resources = []
other_resources = []

remove_build_dir = True

##################################################################
### Below if you edit variables, you could mess up the program ###
##################################################################

include_all = []
for folder in data_files:
    if folder[1][0] == '*':
        include_all.append(folder)

for folder in include_all:
    data_files.remove(folder)

for i in range(len(include_all)):
    include_all[i] = include_all[i][0]

for folder in include_all:
    for root, dirs, files in os.walk(folder):
        rel_files = []
        for file in files:
            rel_files.append(os.path.join(root, file))
        data_files.append((root, rel_files))

class Target(object):
    """ A simple class that holds information on our executable file. """
    def __init__(self, **kw):
        """ Default class constructor. Update as you need. """
        self.__dict__.update(kw)

##############################
### Distutils setup script ###
##############################

Target_1 = Target(
    # what to build
    name = name,
    version = version,
    author = author,
    copyright = copyright,
    company_name = company,
    script = script,
    dest_base = dest_file,
    icon_resources = icon_resources,
    bitmap_resources = bitmap_resources,
    other_resources = other_resources,
    )

setup(
    data_files = data_files,

    zipfile = None,
    console = [Target_1],
    windows = [],

    options = {"py2exe":{
                    "compressed": 0,
                    "optimize": 2,
                    "bundle_files": 1,
                    "dist_dir": dest_folder,
                    "includes": includes,
                    "excludes": excludes,
                    "packages": packages,
                    "dll_excludes": dll_excludes,
                    "xref": False,
                    "skip_archive": False,
                    "ascii": False
                    }
             },
)

if remove_build_dir:
    print 'Removing build directory'
    shutil.rmtree('build')
# If everything went okay, this should come up.
print('\nConversion successful! Exiting...')