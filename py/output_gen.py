#!/usr/bin/env python3
################################################################################
# @file   output_gen.py
# @author Jay Convertino(johnathan.convertino.1@us.af.mil)
# @date   2024.04.24
# @brief  parse yaml file to execute built in tools
#
# @license MIT
# Copyright 2024 Jay Convertino
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
################################################################################

import os
import sys
import shutil
import argparse
import re

def main():
  args = parse_args(sys.argv[1:])

  filters = [r'\.dtb$', r'Image$']

  #copy bootfs to new location
  src_bootfs_dir = os.getcwd() + '/' + args.bootfs + "/" + args.project_name + "/" + "BOOTFS"
  dest_bootfs_dir =  os.getcwd() + '/' + args.dest + "/" + args.project_name + "/" + "bootfs"

  #remove bootfs destination if it exists
  try:
    shutil.rmtree(dest_bootfs_dir, ignore_errors=True)
  except Exception as e:
    print("ERROR: ", e)
    return ~0

  #copy dir and files over
  try:
    shutil.copytree(src_bootfs_dir, dest_bootfs_dir)
  except Exception as e:
    print("ERROR: ", e)
    return ~0

  #copy rootfs to new location
  src_rootfs_dir = os.getcwd() + '/' + args.rootfs + "/" + args.project_name + "/" + "images"
  dest_rootfs_dir = os.getcwd() + '/' + args.dest + "/" + args.project_name + "/" + "rootfs"

  #remove rootfs destination if it exists
  try:
    shutil.rmtree(dest_rootfs_dir, ignore_errors=True)
  except Exception as e:
    print("ERROR: ", e)
    return ~0

  #copy dir and files over
  try:
    shutil.copytree(src_rootfs_dir,  dest_rootfs_dir)
  except Exception as e:
    print("ERROR: ", e)
    return ~0

  #move list of filtered files from rootfs to bootfs
  for dir_file in os.listdir(dest_rootfs_dir):
    for regexp in filters:
      if re.search(regexp, dir_file):
        try:
          shutil.move(src = dest_rootfs_dir + "/" + dir_file, dst = dest_bootfs_dir + "/" + dir_file)
        except Exception as e:
          print("ERROR: ", e)
          return ~0

def parse_args(argv):
  parser = argparse.ArgumentParser(description='Generate dest/project rootfs and bootfs folder in current directory.')

  parser.add_argument('project_name', action='store',   default=None,                                help='Project name to use for output folder output/project_name.')
  parser.add_argument('--rootfs',     action='store',   default=None, dest='rootfs',  required=True, help='Path to rootfs build result.')
  parser.add_argument('--bootfs',     action='store',   default=None, dest='bootfs',  required=True, help='Path to bootfs build result.')
  parser.add_argument('--dest',       action='store',   default=None, dest='dest',    required=True, help='Path to move results to and put in subfolder project.')

  return parser.parse_args()

if __name__=="__main__":
  main()
