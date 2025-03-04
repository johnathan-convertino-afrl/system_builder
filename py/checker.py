##!/usr/bin/env python3
#################################################################################
## @file   checker.py
## @author Jay Convertino(johnathan.convertino.1@us.af.mil)
## @date   2024.07.17
## @brief  parse yaml file to check for tools
##
## @license MIT
## Copyright 2024 Jay Convertino
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to
## deal in the Software without restriction, including without limitation the
## rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
## sell copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
## FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
## IN THE SOFTWARE.
#################################################################################
#import yaml
#import subprocess
#import os
#import pathlib
#import shutil
#import sys
#import logging
#import threading
#import re
#import time

#try:
  #import pkgconfig
#except ImportError:
  #print("REQUIREMENT MISSING: pkgconfig, pip install pkgconfig")
  #exit(0)

#logger = logging.getLogger(__name__)

#class sal:
  #def __init__(self, yaml_data, dryrun = False):
    #self._yaml_data = yaml_data
    #self._dryrun = dryrun
    #self._command_template = None
    #self._projects = None
    #self._threads  = []
    #self._processes = []
    #self._failed = False
    #self._thread_lock = None
    #self._items = 0
    #self._items_done = 0
    #self._project_name = "None"

  #def stop(self):
    #self._failed = True

    #if self._dryrun is False:
      #for p in self._processes:
        #p.terminate()

    #logger.info(f"Thread terminate sent to stop builders.")

  ## run the steps to build parts of targets
  #def run(self):
    #try:
      #self._gen_build_cmds()
    #except Exception as e: raise

    #try:
      #self._process()
    #except Exception as e: raise

    #try:
      #self._execute()
    #except Exception as e: raise

  #def list(self):
    #try:
      #self._gen_build_cmds()
    #except Exception as e: raise

    #print('\n' + f"AVAILABLE YAML COMMANDS FOR BUILD" + '\n')
    #for tool, commands in self._command_template.items():
      #options = []
      #for command, method in commands.items():
        #options.extend([word for word in method if word.count('}')])

      #str_options = ' '.join(options)

      #str_options = str_options.replace('{_project_name}', '')

      #str_options = str_options.replace('{_pwd}', '')

      #str_options = re.findall(r'\{(.*?)\}', str_options)

      #filter_options = list(set(str_options))

      #print(f"COMMAND: {tool:<16} OPTIONS: {filter_options}")

  #def _gen_build_cmds(self):
    #try:
      #stream = open(self._yaml_build_cmds_file, 'r')
    #except Exception as e: raise

    #loaded = None

    #try:
      #loaded = yaml.safe_load(stream)
    #except Exception as e:
      #stream.close()
      #raise

    #self._command_template = loaded

    #logger.debug(self._command_template)

    #stream.close()

  ## create dict of dicts that contains lists with lists of lists to execute with subprocess
  ## {'project': { 'concurrent': [[["make", "def_config"], ["make"]], [["fusesoc", "run", "--build", "--target", "zed_blinky", "::blinky:1.0.0"]]], 'sequential': [[]]}}
  #def _process(self):

    #if self._command_template is None:
      #raise Exception("Command template is None")

    ##filter target into updated dictionary if it was selected
    #if self._target != None:
      #try:
        #self._yaml_data = { self._target: self._yaml_data[self._target]}
      #except KeyError:
        #raise Exception(f"Target: {self._target}, does not exist.")

    #self._projects = {}

    #for project, parts in self._yaml_data.items():
      #project_run_type = {}

      #for run_type, part in parts.items():
        #project_parts = []

        #for part, command in part.items():
          #try:
            #command_template = self._command_template[part].values()
          #except KeyError:
            #raise Exception(f"No build rule for part: {part}.")

          #command.update({'_pwd' : os.getcwd()})

          #command.update({'_project_name' : project})

          #part_commands = []

          #for commands in command_template:
            #populate_command = []

            #string_command = ' '.join(commands)

            #list_command = list(string_command.format_map(command).split(" "))

            #part_commands.append(list_command)

            #logger.debug(part_commands)

          #project_parts.append(part_commands)

        #project_run_type[run_type] = project_parts

      #self._projects[project] = project_run_type

      #logger.info(f"Added commands for project: {project}")

  ##call subprocess as a thread and add it to a list of threads for wait to check on.
  ##iterate over projects avaiable and execute commands per project
  #def _execute(self):
    #if self._projects == None:
      #raise Exception("NO PROJECTS AVAILABLE FOR BUILDER")

    #threading.excepthook = self._thread_exception

    #self._thread_lock = threading.Lock()

    #for project, run_types in self._projects.items():
      #logger.info(f"Starting build for project: {project}")

      #self._items = self._project_cmd_count(run_types)

      #self._items_done = 0

      #self._threads.clear()

      #self._project_name = project

      #bar_thread = threading.Thread(target=self._bar_thread, name="bar")

      #bar_thread.start()

      #for run_type, commands in run_types.items():
        #if run_type == 'concurrent':
          #for command_list in commands:
            #logger.debug("CONCURRENT: " + str(command_list))
            #thread = threading.Thread(target=self._subprocess, name=project, args=[command_list])

            #self._threads.append(thread)

            #thread.start()

            #time.sleep(2)

          #for t in self._threads:
            #t.join()

          #if self._failed:
            #raise Exception(f"One or more threads failed.")

        #elif run_type == 'sequential':
          #for command_list in commands:
            #logger.debug("SEQUENTIAL: " + str(command_list))

            #try:
              #self._subprocess(command_list)
            #except Exception as e:
              #self._failed = True
              #time.sleep(2)
              #raise

        #else:
          #raise Exception(f"RUN_TYPE {run_type} is not a valid selection")

      #bar_thread.join()

  #def _subprocess(self, list_of_commands):
    #for command in list_of_commands:
      #process = None
      #cmd_output = None
      #cmd_error = None

      #if self._failed:
        #raise Exception(f"Previous build process failed, aborting: {' '.join(command)}")

      #logger.info(f"Executing command: {' '.join(command)}")

      #if self._dryrun is False:
        #try:
          #process = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(pathlib.Path.cwd()))
          #self._processes.append(process)
          #cmd_output, cmd_error = process.communicate()
          #exception = process.poll()
          #if exception:
            #if cmd_error:
              #for line in cmd_error.split('\n'):
                #if len(line):
                  #logger.error(line)
            #raise Exception(f"Issue executing command: {' '.join(command)}")
        #except Exception as e: raise

        #if cmd_output:
          #for line in cmd_output.split('\n'):
            #logger.debug(line)

      #with self._thread_lock:
        #self._items_done = self._items_done + 1

        #if self._dryrun is False:
          #self._processes.remove(process)

        #time.sleep(1)

        #logger.info(f"Completed command: {' '.join(command)}")

  #def _project_cmd_count(self, run_types):
    #count = 0

    #for run_type, commands in run_types.items():
      #for command_list in commands:
        #count = count + (len(command_list))

    #return count

  #def _thread_exception(self, args):
    #self._failed = True

    #if self._dryrun is False:
      #for p in self._processes:
        #p.terminate()

    #logger.error(f"Build failed, terminated subprocess and program. {str(args.exc_value)}")

  #def _bar_thread(self):
    #status = "BUILDING"
    #bar = progressbar.ProgressBar(widgets=[progressbar.Timer(format=' [%(elapsed)s] '), progressbar.Percentage(), " ", progressbar.GranularBar(markers='.#', left='[', right='] '), progressbar.Variable('Status'), " | ", progressbar.Variable('Target')], max_value=self._items).start()

    #bar.update(Status=f"{status:^8}")

    #while((self._items_done < self._items) and (self._failed == False)):
      #time.sleep(0.1)
      #bar.update(Target=f"{self._project_name:<64}")
      #bar.update(self._items_done)

    #if self._failed:
      #status = "ERROR"
    #else:
      #status = "SUCCESS"

    #bar.update(Status=f"{status:^8}")
    #bar.finish(dirty=self._failed)

