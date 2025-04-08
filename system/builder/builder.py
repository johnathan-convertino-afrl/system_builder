#******************************************************************************
# file:    builder.py
#
# author:  JAY CONVERTINO
#
# date:    2025/03/08
#
# about:   Brief
# parse yaml file to execute build tools
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
#******************************************************************************
import yaml
import subprocess
import os
import pathlib
import shutil
import sys
import logging
import threading
import re
import time

from .version import __version__

try:
  import progressbar
except ImportError:
  print("REQUIREMENT MISSING: progressbar2, pip install progressbar2")
  exit(0)

logger = logging.getLogger(__name__)

# Class: commandCompiler
# Parse yaml files into commands for command executor
class commandCompiler:
  # Method: __init__
  # Setup class
  def __init__(self, yaml_projects = None, yaml_commands = None, target = None):
    self._yaml_commands = yaml_commands
    self._yaml_projects = yaml_projects
    self._target = target
    self._command_template = None
    self._project_template = None
    self._projects = None

    logger.info(f"{self.__class__.__name__:<24} : VERSION {__version__}")

  # Method: listCommands
  # Print a list of all the commands available
  def listCommands(self):
    try:
      self._command_template = self._load_yaml(self._yaml_commands)
    except Exception as e: raise

    print('\n' + f"AVAILABLE YAML COMMANDS FOR BUILD" + '\n')
    for tool, commands in self._command_template.items():
      options = []
      for command, method in commands.items():
        options.extend([word for word in method if word.count('}')])

      str_options = ' '.join(options)

      str_options = str_options.replace('{_project_name}', '')

      str_options = str_options.replace('{_pwd}', '')

      str_options = re.findall(r'\{(.*?)\}', str_options)

      filter_options = list(set(str_options))

      print(f"COMMAND: {tool:<16} OPTIONS: {filter_options}")

  # Method: listProjects
  # Print a list of all the
  def listProjects(self):
    try:
      self._project_tempate = self._load_yaml(self._yaml_projects)
    except Exception as e: raise

    print('\n' + f"SYSTEM BUILDER TARGETS FROM {self._yaml_projects.upper()}" + '\n')

    for target, value in self._project_tempate.items():
      print(f"TARGET: {target}")

  # Method: clear
  # Clear results of create and current yaml file pointer.
  def clear(self):
    self._yaml_commands = None
    self._yaml_projects = None
    self._command_template = None
    self._projects = None

  # Method: setProjects
  # Set a yaml file for project commands
  def setProjects(self, yaml_projects):
    self._yaml_projects = yaml_projects

  # Method: setCommands
  # Set a yaml file for commands available
  def setCommands(self, yaml_commands):
    self._yaml_commands = yaml_commands

  # Method: setProjectsWithYamlData
  # Set internal variable with yaml data directly.
  def setProjectsWithYamlData(self, yaml_data):
    self._project_template = yaml_data

  # Method: setCommandsWithYamlData
  # Set internal variable with yaml data directly.
  def setCommandsWithYamlData(self, yaml_data):
    self._command_template = yaml_data

  # Method: create
  # Pass a yaml file to use for processing into format for commandExecutor.
  def create(self, yaml_projects = None, yaml_commands = None, target = None):
    if(yaml_commands is None and self._yaml_commands is None and self._command_tempate is None):
      logger.error(f"{self.__class__.__name__:<24} : YAML COMMANDS HAS NOT BEEN SET")
      raise TypeError("YAML COMMANDS FILE HAS NOT BEEN SET")

    if(yaml_projects is None and self._yaml_projects is None and self._project_tempate is None):
      logger.error(f"{self.__class__.__name__:<24} : YAML PROJECTS HAS NOT BEEN SET")
      raise TypeError("YAML PROJECTS FILE HAS NOT BEEN SET")

    if(yaml_commands is not None):
      self._yaml_commands = yaml_commands

    if(yaml_projects is not None):
      self._yaml_projects = yaml_projects

    if(target is not None):
      self._target = target

    logger.debug(f'{self.__class__.__name__:<24} : LOADING YAML COMMANDS FILE {self._yaml_commands.upper()}')

    try:
      if self._command_template is None:
        self._command_template = self._load_yaml(self._yaml_commands)
    except Exception as e: raise

    logger.debug(f'{self.__class__.__name__:<24} : LOADING YAML PROJECTS FILE {self._yaml_projects.upper()}')

    try:
      if self._project_template is None:
        self._project_template = self._load_yaml(self._yaml_projects)
    except Exception as e: raise

    logger.debug(f'{self.__class__.__name__:<24} : CHECKING FOR TARGET {self._target}')

    try:
      self._checkTarget()
    except Exception as e: raise

    logger.debug(f'{self.__class__.__name__:<24} : PROCESSING YAML PROJECT AND COMMANDS TO CREATE BUILD SCRIPT')

    try:
      self._process()
    except Exception as e: raise

  # Method: getResult
  # Return dict of dicts that contains lists with lists of lists to execute with subprocess
  # {'project': { 'concurrent': [[["make", "def_config"], ["make"]], [["fusesoc", "run",
  # "--build", "--target", "zed_blinky", "::blinky:1.0.0"]]], 'sequential': [[]]}}
  def getResult(self):
    if(self._projects is None):
      logger.error(f"{self.__class__.__name__:<24} : PROJECTS IS NONE, RUN CREATE BEFORE TRYING TO GET RESULTS.")
      raise ValueError("PROJECTS IS NONE")

    return self._projects

  # Method: _checkTarget
  def _checkTarget(self):
    #filter target into updated dictionary if it was selected
    if self._target != None:
      try:
        self._project_template = {self._target: self._project_template[self._target]}
      except KeyError as e:
        logger.exception(f"{self.__class__.__name__:<24} : TARGET : {target}, DOES NOT EXIST.", exc_info=e)
        raise RuntimeError("TARGET IS INVALID")

  # Method: _process
  # Create dict of dicts that contains lists with lists of lists to execute with subprocess
  # {'project': { 'concurrent': [[["make", "def_config"], ["make"]], [["fusesoc", "run",
  # "--build", "--target", "zed_blinky", "::blinky:1.0.0"]]], 'sequential': [[]]}}
  def _process(self):

    if self._command_template is None:
      logger.error(f"{self.__class__.__name__:<24} : Command template is None")
      raise ValueError("COMMAND TEMPLATE IS NONE")

    self._projects = {}

    for project, parts in self._project_template.items():
      project_run_type = {}

      for run_type, part in parts.items():
        project_parts = []

        for part, command in part.items():

          try:
            command_template = self._command_template[part].values()
          except KeyError as e:
            logger.exception(f"{self.__class__.__name__:<24} : NO BUILD RULE FOR PART: {part}.", exc_info=e)
            raise

          command.update({'_pwd' : os.getcwd()})

          command.update({'_project_name' : project})

          part_commands = []

          for commands in command_template:
            populate_command = []

            string_command = ' '.join(commands)

            list_command = list(string_command.format_map(command).split(" "))

            part_commands.append(list_command)

            logger.debug(part_commands)

          project_parts.append(part_commands)

        project_run_type[run_type] = project_parts

      self._projects[project] = project_run_type

      logger.info(f"{self.__class__.__name__:<24} : Added Commands For Project: {project}")

  # Method: _load_yaml
  # Internal function that will load the yaml file that contains project commands or commands.
  def _load_yaml(self, yaml_file):
    try:
      stream = open(yaml_file, 'r')
    except Exception as e: raise

    loaded = None

    try:
      loaded = yaml.safe_load(stream)
    except Exception as e:
      stream.close()
      raise

    logger.debug(loaded)

    stream.close()

    return loaded

# Class: commandExecutor
# Execute commands create from commandCompileris not a valid selection
class commandExecutor:
  def __init__(self, projects = None, dryrun = False):
    self._projects = projects
    self._dryrun = dryrun
    self._failed = False
    self._threads = []
    self._processes = []
    self._thread_lock = None
    self._items = 0
    self._items_done = 0
    self._project_name = "None"

    logger.info(f"{self.__class__.__name__:<24} : VERSION {__version__}")

  # Method: clear
  # Clear state of commandExecutor to init with no values passed
  def clear(self):
    if(self.completed or self.failed):
      self._projects = None
      self._failed = False
      self._threads.clear()
      self._processes.clear()
      self._thread_lock = None
      self._dryrun = False
      self._items = 0
      self._items_done = 0
      self._project_name = "None"
    else:
      logger.error(f"{self.__class__.__name__:<24} : CAN NOT CLEAR WHILE ITEMS ARE NOT COMPLETE OR EXECUTOR HAS NOT FAILED")
      raise RuntimeError("CAN NOT CLEAR WHILE ITEMS ARE NOT COMPLETE OR EXECUTOR HAS NOT FAILED")

  # Method: completed
  # return a bool if all items have been completed.
  def completed(self):
    return self._items == self._items_done

  # Method: failed
  # return a bool indicating failure
  def failed(self):
    return self._failed

  # Method: stop
  # Kill and current processes in build threads
  def stop(self):
    self._failed = True

    if self._dryrun is False:
      for p in self._processes:
        p.kill()

    logger.info(f"{self.__class__.__name__:<24} : Thread kill sent to stop builders.")

  # Method: setDryrun
  # Setting to True sets the project run everything up to the subprocess.Popen call, which is skipped.
  def setDryrun(dryrun = False):
    self._dryrun = dryrun

  # Method: setProjects
  # Set the projects for the executor to build
  def setProjects(self, projects):
    self._projects = projects

  # Method: runProject
  # Call the internal execute method to start calling up each of the projects to build.
  def runProject(self, projects = None):
    if(self._projects is None and projects is None):
      logger.error(f"{self.__class__.__name__:<24} : NO PROJECT(S) ARE AVAILABLE TO RUN")
      raise ValueError("NO PROJECT(S) ARE AVAILABLE TO RUN")

    try:
      self._execute()
    except Exception as e: raise

  # Method: _execute
  # Call subprocess as a thread an_gen_build_cmdsd add it to a list of threads for wait to check on.
  # iterate over projects avaiable and execute commands per project
  def _execute(self):
    if self._projects == None:
      logger.error(f"{self.__class__.__name__:<24} : NO PROJECTS AVAILABLE FOR BUILDER")
      raise RuntimeError("NO PROJECTS SPECIFIED")

    threading.excepthook = self._thread_exception

    self._thread_lock = threading.Lock()

    for project, run_types in self._projects.items():
      logger.info(f"{self.__class__.__name__:<24} : Starting build for project: {project}")

      self._items = self._project_cmd_count(run_types)

      self._items_done = 0

      self._threads.clear()

      self._project_name = project

      bar_thread = threading.Thread(target=self._bar_thread, name="bar")

      bar_thread.start()

      for run_type, commands in run_types.items():
        if run_type == 'concurrent':
          for command_list in commands:
            logger.debug("CONCURRENT: " + str(command_list))
            thread = threading.Thread(target=self._subprocess, name=project, args=[command_list])

            self._threads.append(thread)

            thread.start()

            time.sleep(2)

          for t in self._threads:
            t.join()

          if self._failed:
            logger.error(f"{self.__class__.__name__:<24} : ONE OR MORE THREADS FAILED.")
            raise RuntimeError("THREAD HAS FAILED")

        elif run_type == 'sequential':
          for command_list in commands:
            logger.debug("SEQUENTIAL: " + str(command_list))

            try:
              self._subprocess(command_list)
            except Exception as e:
              self._failed = True
              time.sleep(2)
              raise

        else:
          logger.error(f"{self.__class__.__name__:<24} : RUN_TYPE {run_type} IS NOT A VALID SELECTION")
          raise TypeError("INVALID RUNTYPE")

      bar_thread.join()

  # Method: _subprocess
  # Responsible for taking a list of commands and launching threads concurrently
  # or singurely.
  def _subprocess(self, list_of_commands):

    for command in list_of_commands:
      process = None
      cmd_output = None
      cmd_error = None
      cmd_cwd_path  = str(pathlib.Path.cwd())
      cmd_env = None
      skip_exists = True

      for item in command:
        if "__CWD__" in item:
          cmd_cwd_path = item[len("__CWD__"):]
          command.remove(item)

      for item in command:
        if "__ENV_PATH__" in item:
          cmd_env = os.environ.copy()
          cmd_env["PATH"] = f"{item[len('__ENV_PATH__'):]}:{cmd_env['PATH']}"
          command.remove(item)

      for item in command:
        if "__CHECK_SKIP__" in item:
          check_item = item[len("__CHECK_SKIP__"):]
          skip_exists = os.path.exists(check_item)
          if skip_exists:
             with self._thread_lock:
              self._items_done = self._items_done + len(list_of_commands);

              time.sleep(1)

              logger.info(f"{self.__class__.__name__:<24} : Command skipped, following exists: {check_item}")

              return
          else:
            with self._thread_lock:
              self._items_done = self._items_done + 1;

      if not skip_exists:
        continue

      if self._failed:
        logger.error(f"{self.__class__.__name__:<24} : PREVIOUS BUILD PROCESS FAILED, ABORTING : {' '.join(command)}")
        raise RuntimeError("PREVIOUS BUILD FAILED")

      logger.info(f"{self.__class__.__name__:<24} : Executing command: {' '.join(command)}")

      if self._dryrun is False:
        try:
          process = subprocess.Popen(command, env = cmd_env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cmd_cwd_path)
          self._processes.append(process)
          cmd_output, cmd_error = process.communicate()
          exception = process.poll()
          if exception:
            if cmd_error:
              for line in cmd_error.split('\n'):
                if len(line):
                  logger.exception(line)
            logger.error(f"{self.__class__.__name__:<24} : ISSUE EXECUTING COMMAND : {' '.join(command)}")
            raise RuntimeError("ISSUE EXECUTING COMMAND")
        except Exception as e: raise

        if cmd_output:
          for line in cmd_output.split('\n'):
            logger.debug(line)

      with self._thread_lock:
        self._items_done = self._items_done + 1

        if self._dryrun is False:
          self._processes.remove(process)

        time.sleep(1)

        logger.info(f"{self.__class__.__name__:<24} : Completed Command : {' '.join(command)}")

  # Method: _project_cmd_count
  # Number of commands in a project.
  def _project_cmd_count(self, run_types):
    count = 0

    for run_type, commands in run_types.items():
      for command_list in commands:
        count = count + (len(command_list))

    return count

  # Method: _thread_exception
  # Used to kill all threads once one has failed.
  def _thread_exception(self, args):
    self._failed = True

    if self._dryrun is False:
      for p in self._processes:
        p.kill()

    logger.error(f"{self.__class__.__name__:<24} : BUILD FAILED, TERMINATED SUBPROCESS AND PROGRAM. {str(args.exc_value)}")

  # Method: _bar_thread
  # Creates progress bar display in terminal for end user display.
  def _bar_thread(self):
    status = "BUILDING"
    bar = progressbar.ProgressBar(widgets=[progressbar.Timer(format=' [%(elapsed)s] '), progressbar.Percentage(), " ", progressbar.GranularBar(markers='.#', left='[', right='] '), progressbar.Variable('Status'), " | ", progressbar.Variable('Target')], max_value=self._items).start()

    bar.update(Status=f"{status:^8}")

    while((self._items_done < self._items) and (self._failed == False)):
      size = os.get_terminal_size().columns-80
      if size < 0:
        self._failed = True
        break

      bar.update(Target=f"{self._project_name[:size]:<{size}}")
      bar.update(self._items_done)

    if self._failed:
      status = "ERROR"
    else:
      status = "SUCCESS"

    bar.update(Status=f"{status:^8}")
    bar.finish(dirty=self._failed)

class commandDependencies:
  def __init__(self):
    pass

  def clear(self):
    pass

  def setList(self, yaml_file):
    pass

  def check(self):
    pass

  def result(self):
    pass









