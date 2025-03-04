# AFRL System Builder
### Python System Builder for Projects

---

author: Jay Convertino

date: 2024.12.16

details: Generic python application that uses YAML to script builds and define commands.

license: MIT

---

![logo_img](img/logo.png)

## TODO
  - Document

## Quick Info
  - Document

## Release Versions
### Current
  - none

### Past
  - none

## Requirements
### system_build.py
  - gitpython
  - progressbar2

### OS
  - Tested on Ubuntu 22.04

## Quick Start
  0. Clone this repo

## Usage
### System Builder
System builder is a python script that will build all targets in order based on a yaml script. By default this is build.yml if it is not specified. It also checks dependencies, cleans toplevel untracked artifacts, and pulls subrepos.

Each target will be built with its current status show in its own progress bar. This shows the time elapsed, percent complete, status, and name of current target being build.

Example of output to terminal below (formatted to fit this document).

##### Successful build:

```
Checking for dependencies...
Checking for dependencies complete.
Checking for submodules...
Checking for submodules complete.
Starting build system targets...

[0:13:23] 100% |████████████████| Status: SUCCESS  | Target: zed_fmcomms2-3_linux_busybox_sdcard
[0:13:37] 100% |████████████████| Status: SUCCESS  | Target: zc702_fmcomms2-3_linux_busybox_sdcard
[0:13:38] 100% |████████████████| Status: SUCCESS  | Target: zc706_fmcomms2-3_linux_busybox_sdcard

Completed build system targets.
```

##### Failed build:

```
Starting build system targets...

 [0:26:36]  85% |█████████▓    | Status:  ERROR   | Target: zcu102_fmcomms5_linux_busybox_sdcard

ERROR: build system failure, see log file log/240513_1715617815.log.
```

#### Options

```
  --list_targets       List all targets.
  --list_commands      List all available yaml build commands.
  --list_deps          List all available dependencies.
  --clean              remove all generated outputs, including logs.
  --deps DEPS_FILE     Path to dependencies txt file, used to check if command
                       line applications exist.
  --build CONFIG_FILE  Path to build configuration yaml file. build.yml is
                       default.
  --target TARGET      Target name from list. None will build all targets by
                       default.
  --debug              Turn on debug logging messages
  --dryrun             Run build without executing commands.
  --noupdate           Run build without updating submodules.
  --nodepcheck         Run build without checking dependencies.
```

#### build.yml
build.yml (default value system builder looks for) file specifies targets with parts that contain commands for builds. These parts can be concurrent for multithreading, or sequenctial for one at a time. The order these are executed is from the top down. Meaning the top command will be executed before the one below it.

Sample build.yml

```
zed_fmcomms2-3_linux_busybox_sdcard:
  concurrent:
    fusesoc: &fusesoc_fmcomms2-3
      path: hdl
      project: AFRL:project:fmcomms2-3:1.0.0
      target: zed_bootgen
    buildroot: &buildroot_fmcomms2-3
      path: sw/linux/buildroot-afrl
      config: zynq_zed_ad_fmcomms2-3_defconfig
  sequential:
    script: &output_files_fmcomms2-3
      exec: python
      file: py/output_gen.py
      args: "--rootfs output/linux --bootfs output/hdl --dest output/sdcard"
    genimage:
      path: img_cfg
zc702_fmcomms2-3_linux_busybox_sdcard:
  concurrent:
    fusesoc:
      <<: *fusesoc_fmcomms2-3
      target: zc702_bootgen
    buildroot:
      <<: *buildroot_fmcomms2-3
      config: zynq_zc702_ad_fmcomms2-3_defconfig
  sequential:
    script:
      <<: *output_files_fmcomms2-3
    genimage:
      path: img_cfg
```

#### deps.txt
deps.txt (default value system builder looks for) file specifies any executable dependency of the project. These are list line by line in a simple text file. No version checks at the moment. If any are missing the application will print out the missing executable and quit.

Sample deps.txt

```
genimage
fusesoc
make
quartus_cpf
quartus
mkimage
vivado
xsct
bootgen
gcc
```

## Help
### General
Look at the build log log/DATE_TIME.log for hints on where the error happened. Add the --debug option to the run to get all output dumped to the log file.
