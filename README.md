# AFRL System Builder
### Python System Builder for Projects

![logo_img](docs/manual/img/AFRL.png)

---

author: Jay Convertino

date: 2024.12.16

details: Generic python library that uses YAML to script project builds and define commands for them.

license: MIT

---
## TODO
  - Cleanup logger code
  - Better kills(more hit points)
  - Documentation

## Version
### Current
  - v0.5.1 - Fix for error output vs exception(NoneType: None).

### Past
  - v0.5.0 - first proper library
  - v0.0.0

### DOCUMENTATION
  For detailed usage information, please navigate to one of the following sources. They are the same, just in a different format.

  - [system_builder.pdf](docs/manual/system_builder.pdf)
  - [github page](https://johnathan-convertino-afrl.github.io/system_builder/)

## Requirements
### python
  - gitpython
  - progressbar2

### OS
  - Tested on Ubuntu 22.04, 24.04

## Usage

### Install
  0. Clone this repo
  1. pip install --break-system-packages -e .

### System Builder
System builder is a python library that will build all target projects in order based on a yaml commands and a yaml projects file. The yaml commands file gives a command and the list of actions to complete that
command. The yaml projects file contains the steps to build the project using the commands. The library is used by creator python scripts that interact with the end user.

Each target project will be built with its current status show in its own progress bar. This shows the time elapsed, percent complete, status, and name of current target being build.

Example of output to terminal below (formatted to fit this document).

##### Successful build:

```
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

#### Projects YAML file
The projects yaml file specifies target projects with parts that contain commands for builds. These parts can be concurrent for multithreading, or sequenctial for one at a time. The order these are executed is from the top down. Meaning the top command will be executed before the one below it.

Sample below:

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

#### Commands YAML file
The commands yaml file specifies commands for projects.

Sample below:

```
fusesoc:
  cmd_0: ["__CHECK_SKIP__{_pwd}/output/hdl/{_project_name}/AFRL_project_veronica_axi_baremetal_1.0.0.bit"]
  cmd_1: ["fusesoc", "--cores-root", "{path}", "run", "--build", "--work-root", "output/hdl/{_project_name}", "--target", "{target}", "{project}"]
script:
  cmd_1: ["{exec}", "{file}", "{_project_name}", "{args}"]
gcc_riscv32:
  cmd_0: ["__CHECK_SKIP__{_pwd}/output/bin/riscv/bin/riscv32-unknown-elf-gcc"]
  cmd_1: ["make", "-C", "{_pwd}/{path}", "clean"]
  cmd_2: ["__CWD__{_pwd}/{path}", "./configure", "--prefix={_pwd}/output/bin/riscv", "--disable-linux", "--with-arch=rv32imac", "--with-abi-ilp32"]
  cmd_3: ["make", "-C", "{_pwd}/{path}", "-j", "8"]
openocd_riscv:
  cmd_0: ["__CHECK_SKIP__{_pwd}/output/bin/openocd/bin/openocd"]
  #cmd_1: ["__CWD__{_pwd}/{path}", "git", "apply", "--ignore-whitespace", "../patch/pmpregs.patch"]
  cmd_2: ["__CWD__{_pwd}/{path}", "./bootstrap"]
  cmd_3: ["__CWD__{_pwd}/{path}", "./configure", "--prefix={_pwd}/output/bin/openocd", "--enable-ftdi", "--enable-dummy", "--enable-jtag_vpi"]
  cmd_4: ["make", "-C", "{_pwd}/{path}", "-j", "8"]
  cmd_5: ["make", "install", "-C", "{_pwd}/{path}"]
fpga_baremetal_examples:
  cmd_0: ["__CHECK_SKIP__{_pwd}/output/apps"]
  cmd_1: ["mkdir", "-p", "{_pwd}/{path}/cmake"]
  cmd_2: ["__CWD__{_pwd}/{path}/cmake", "__ENV_PATH__{_pwd}/output/bin/riscv/bin/", "cmake", "../", "-DCMAKE_RUNTIME_OUTPUT_DIRECTORY={_pwd}/output/apps", "-DCMAKE_PREFIX_PATH={_pwd}/output/bin/riscv/bin/", "-DBUILD_EXAMPLES_ALL=ON", "-DCMAKE_TOOLCHAIN_FILE={_pwd}/{path}/arch/riscv/riscv.cmake"]
  cmd_3: ["__ENV_PATH__{_pwd}/output/bin/riscv/bin/", "make", "-C", "{_pwd}/{path}/cmake"]
buildroot:
  cmd_1: ["rm", "-rf", "{_pwd}/output/linux/{_project_name}"]
  cmd_2: ["make", "-C", "{path}", "distclean"]
  cmd_3: ["make", "O={_pwd}/output/linux/{_project_name}", "-C", "{path}", "{config}"]
  cmd_4: ["make", "O={_pwd}/output/linux/{_project_name}", "-C", "{path}"]
genimage:
  cmd_1: ["mkdir", "-p", "{_pwd}/output/genimage/tmp/{_project_name}"]
  cmd_2: ["genimage", "--config", "{path}/{_project_name}.cfg"]
```

## Tests
The tests folder contains an example creator python script. This will execute a few different simple builds using the system builder library. This is an
incomplete set of tests at the moment.

## Help
### General
Look at the build log log/DATE_TIME.log for hints on where the error happened. Add the --debug option to the run to get all output dumped to the log file.
