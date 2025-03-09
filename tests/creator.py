#!/usr/bin/env python3
#*******************************************************************************
# file:    creator.py
#
# author:  JAY CONVERTINO
#
# date:    2025/03/08
#
# about:   Brief
# Example program for using system.builder library.
#
# @license MIT
# Copyright 2025 Jay Convertino
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
#*******************************************************************************

import yaml
import subprocess
import os
import pathlib
import shutil
import sys
import argparse
import logging
import time

logger = logging.getLogger()

# check for git
try:
  import git
except ImportError:
  print("REQUIREMENT MISSING: gitpython, pip install gitpython")
  exit(0)

sys.path.append("../")

sys.dont_write_bytecode = True

import system.builder

# Function: main
# main execution function
def main():
  args = parse_args(sys.argv[1:])

  if args.clean:
    exit(clean())

  if args.list_deps:
    exit(list_deps(args.deps_file))

  logger_setup(args.debug)

  yaml_data = open_yaml(args.config_file)

  if yaml_data is None:
    exit(~0)

  if args.list_cmds:
    exit(builder.bob("py/build_cmds.yml", yaml_data).list())

  if args.list_all:
    exit(list_projects(yaml_data, args.config_file))

  if args.nodepcheck is False:
    try:
      deps_check(args.deps_file)
    except Exception as e:
      print("Dependencies issue:")
      print(str(e))
      exit(~0)

  if args.noupdate is False:
    submodule_init(os.getcwd())

  print("Starting build system targets...\n")

  bob = builder.bob("py/build_cmds.yml", yaml_data, args.target, args.dryrun)

  try:
    bob.run()
  except KeyboardInterrupt:
    bob.stop()
    time.sleep(1)
    print("\n" + f"Build interrupted with CTRL+C.")
    exit(~0)
  except Exception as e:
    logger.error(str(e))
    time.sleep(1)
    print("\n" + f"ERROR: build system failure, for details, see log file log/{os.path.basename(logger.handlers[0].baseFilename)}")
    exit(~0)

  print("\n" + f"Completed build system targets, for details, see log file log/{os.path.basename(logger.handlers[0].baseFilename)}")

  exit(0)

# Function: list_deps
# open deps text file and print all executable names.
def list_deps(deps_file):
  try:
    deps = open(deps_file, 'r')
  except FileNotFoundError as e:
    print("ERROR :" + str(e))
    return ~0

  deps_list = []

  lines = deps.readlines()

  print("DEPENDENCIES FOR BUILD")
  for line in lines:
    print("CMD EXE: " + line.strip())

  return 0

# Function: deps_check
# Check each line of txt file programs
def deps_check(deps_file):
  try:
    deps = open(deps_file, 'r')
  except FileNotFoundError as e:
    raise Exception(e)

  deps_list = []

  lines = deps.readlines()

  print("Checking for dependencies...")

  for line in lines:
    if shutil.which(line.strip()) is None:
      deps_list.append(line.strip())

  if len(deps_list) > 0:
    raise Exception("\n".join(deps_list))

  print("Checking for dependencies complete.")

# Function: submodule_init
# Make sure submodules have been pulled. If not, pull them.
def submodule_init(repo):
  repo = git.Repo(repo)

  print("Checking for submodules...")

  for submodule in repo.submodules:
    submodule.update(init=True, force=True, recursive=True, keep_going=True)

  print("Checking for submodules complete.")

    # if not submodule.module_exists():
    #   print("Updating submodule in path: " + submodule.abspath)
    #   print("Submodule " + str(submodule.update()) + " pulled")
    #
    # if len(submodule.children()):
    #   submodule_init(submodule)

# open_yaml
# Open the yaml file for processing
def open_yaml(file_name):
  try:
    stream = open(file_name, 'r')
  except:
    print(file_name + " not available.")
    return None

  try:
    yaml_data = yaml.safe_load(stream)
  except yaml.YAMLError as e:
    logger.error("yaml issue")
    for line in str(e).split("\n"):
      logger.error(line)
    print("ERROR: check log for yaml parse error.")
    stream.close()
    return None

  stream.close()
  return yaml_data

# Function: list_projects
# List projects from the yaml file.
def list_projects(yaml, file_name):
  if not len(yaml):
    return ~0

  print('\n' + f"SYSTEM BUILDER TARGETS FROM {file_name.upper()}" + '\n')

  for target, value in yaml.items():
    print(f"TARGET: {target}")

  return 0

# Function: clean
# Clean up folders used for output (output and log)
def clean():
  print("********************************")
  print("** CLEANING UNTRACKED ITEMS")

  repo = git.Repo(os.getcwd())

  if len(repo.ignored(os.listdir())) == 0:
    print("** NOTHING TO REMOVE")

  for item in repo.ignored(os.listdir()):
    if os.path.isfile(item):
      print(f"** REMOVING FILE: {item}")
      os.remove(item)
    else:
      print(f"** REMOVING DIR: {item}")
      shutil.rmtree(item, ignore_errors=True)

  print("** CLEANING COMPLETE")
  print("********************************")

  return 0

# Function: parse_args
# Parse args for tuning build
def parse_args(argv):
  parser = argparse.ArgumentParser(description='Automate projects build using yaml target list.')

  group = parser.add_mutually_exclusive_group()

  group.add_argument('--list_targets',    action='store_true',  default=False,        dest='list_all',    required=False, help='List all targets.')
  group.add_argument('--list_commands',   action='store_true',  default=False,        dest='list_cmds',   required=False, help='List all available yaml build commands.')
  group.add_argument('--list_deps',       action='store_true',  default=False,        dest='list_deps',   required=False, help='List all available dependencies.')
  group.add_argument('--clean',           action='store_true',  default=False,        dest='clean',       required=False, help='remove all generated outputs, including logs.')

  parser.add_argument('--deps',       action='store',       default="deps.txt",   dest='deps_file',   required=False, help='Path to dependencies txt file, used to check if command line applications exist. deps.txt is the default.')
  parser.add_argument('--build',      action='store',       default="build.yml",  dest='config_file', required=False, help='Path to build configuration yaml file. build.yml is the default.')
  parser.add_argument('--target',     action='store',       default=None,         dest='target',      required=False, help='Target name from list. None will build all targets by default.')
  parser.add_argument('--debug',      action='store_true',  default=False,        dest='debug',       required=False, help='Turn on debug logging messages')
  parser.add_argument('--dryrun',     action='store_true',  default=False,        dest='dryrun',      required=False, help='Run build without executing commands.')
  parser.add_argument('--noupdate',   action='store_true',  default=False,        dest='noupdate',    required=False, help='Run build without updating submodules.')
  parser.add_argument('--nodepcheck', action='store_true',  default=False,        dest='nodepcheck',  required=False, help='Run build without checking dependencies.')

  return parser.parse_args()

# Function: logger_setup
# Setup logger for log file
def logger_setup(debug):
  log_name = time.strftime("log/" + "%y%m%d", time.localtime()) + '_' +  str(int(time.mktime(time.localtime()))) + '.log'

  os.makedirs(os.getcwd() + "/log", exist_ok=True)

  if debug:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)

  log_file = logging.FileHandler(filename = log_name, mode = 'w', delay=True)

  if debug:
    log_file.setLevel(logging.DEBUG)
  else:
    log_file.setLevel(logging.INFO)

  format_file = logging.Formatter(fmt = '%(asctime)-12s : %(levelname)-8s : %(message)s', datefmt='%y.%m.%d %H:%M')
  log_file.setFormatter(format_file)

  logger.addHandler(log_file)


# name of main is main
if __name__=="__main__":
  main()
