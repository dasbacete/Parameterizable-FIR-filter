import os
import sys
import yaml as yml

from pathlib import Path
from loguru import logger
from subprocess import Popen, PIPE

_PERM_ELMS = ['.src', 'tb', 'rtl', 'resources', 'sim']


class project:
    name = None
    root = None
    path = None
    sm = None
    rtl = None
    tb = None
    rsc = None

    # Constructor
    def __init__(self, src_path, debug, first_caller):
        self.logger = logger
        self.path = src_path
        if 'PROJ_DIR' in os.environ:
            self.root = Path(os.environ['PROJ_DIR'])
        else:
            logger.critical("Project path is not set, please launch \
                    configuration")
        if first_caller:
            self.cfg_logger(debug)
            logger.info(f"Project path is {os.environ['PROJ_DIR']}")
        src_file = ''
        with open(src_path / '.src', 'r') as f:
            src_file = yml.safe_load(f)
        if 'name' in src_file:
            self.name = src_file['name']
        else:
            logger.critical("Please include a name for the project")
            return
        logger.debug(f"Building {self.name}")
        if 'rtl' in src_file:
            self.rtl = src_file['rtl']
        if 'tb' in src_file:
            self.tb = src_file['tb']
        if 'resources' in src_file:
            self.rsc = src_file['resources']

        proj_list = os.listdir(src_path)
        for el in _PERM_ELMS:
            if el in proj_list:
                proj_list.remove(el)
        if not proj_list:
            logger.debug(f"last module level found {self.name}")
        else:
            self.sm = []
            for sm in proj_list:
                self.sm.append(project(src_path / sm, debug, False))
        logger.debug(f"This is top level {self.im_top( src_path )}")

    def get_rsc(self):
        rsc = {}
        if self.sm:
            for sm in self.sm:
                rsc.update(sm.get_rsc())
        if self.rsc:
            rsc[self.name] = [self.path / 'resources' /
                              file for file in self.rsc]
        return rsc

    def get_tb(self):
        tb = {}
        if self.sm:
            for sm in self.sm:
                tb.update(sm.get_tb())
        if self.tb:
            tb[self.name] = [self.path / 'tb' / file for file in self.tb]
        return tb

    def get_rtl(self):
        rtl = {}
        if self.sm:
            for sm in self.sm:
                rtl.update(sm.get_rtl())
        if self.rtl:
            rtl[self.name] = [self.path / 'rtl' / file for file in self.rtl]
        return rtl

    def compile(self, defs, v):
        rc = 0
        compile_files = []
        rsc = self.get_rsc()
        rtl = self.get_rtl()
        tb = self.get_tb()
        for f in rsc.values():
            compile_files.extend(f)
        for f in rtl.values():
            compile_files.extend(f)
        for f in tb.values():
            compile_files.extend(f)
        defines = None
        if (defs is not None):
            defines = get_defines(defs)
            defines = ' ' + defines
        else:
            defines = ''
        current_dir = os.getcwd()
        os.chdir(self.path)
        if ('sim' not in os.listdir('./')):
            os.mkdir('./sim')
        os.chdir('./sim')
        for f in compile_files:
            cmd = build_compile_cmd(f)
            cmd += defines
            rc = launch(cmd, v)
            if (rc != 0):
                os.chdir(current_dir)
                return rc
        os.chdir(current_dir)
        return rc

    def elaborate(self, top, tb, defs, v):
        rc = 0
        current_dir = os.getcwd()
        os.chdir(self.path)
        if ('sim' not in os.listdir('./')):
            os.mkdir('./sim')
        os.chdir('sim')
        logger.add('hb_elab.log')
        defines = None
        if (defs is not None):
            defines = get_defines(defs)
            defines = ' ' + defines
        else:
            defines = ''
        if (tb is None):
            cmd = f"xelab -top {top} {defines}"
            rc = launch(cmd, v)
            if (rc != 0):
                os.chdir(current_dir)
                return rc
        else:
            cmd = f"xelab -snapshot sim_{self.name} \
-top {tb}  -debug all {defines}"
            rc = launch(cmd, v)
            if (rc != 0):
                os.chdir(current_dir)
                return rc
        os.chdir(current_dir)
        return rc

    # This can be improved by allowing simulation with multiple names and
    # selecting them by tb
    def simulate(self, sw, v):
        current_dir = os.getcwd()
        os.chdir(self.path / 'sim')
        cmd = f"xsim sim_{self.name} \
 --tclbatch {str(self.root)}/prj/scripts/xsim_cfg.tcl "
        rc = launch(cmd, v)
        if (rc != 0):
            os.chdir(current_dir)
            return rc
        if (sw):
            cmd = f"xsim --gui sim_{self.name}.wdb &"
            rc = launch(cmd, v)
            if (rc != 0):
                os.chdir(current_dir)
                return rc
        os.chdir(current_dir)
        return 0

    def show_waveforms(self, v):
        current_dir = os.getcwd()
        os.chdir(self.path / 'sim')
        cmd = f"xsim --gui sim_{self.name}.wdb &"
        rc = launch(cmd, v)
        if (rc != 0):
            os.chdir(current_dir)
            return rc
        os.chdir(current_dir)
        return 0

    def run(self, top, tb, sw, defs, v):
        logger.info("Starting compilation")
        rc = self.compile(defs, v)
        if (rc != 0):
            return rc
        logger.info(f"Starting elaboration. Top: {top}")
        rc = self.elaborate(top, tb, defs, v)
        if (rc != 0):
            return rc
        logger.info(f"Starting simulation. TB: {tb}")
        rc = self.simulate(sw, v)
        if (rc != 0):
            return rc

    def im_top(self, path):
        return self.root.resolve() == Path(os.path.dirname(path)).resolve()

    def cfg_logger(self, debug):
        self.logger.remove()
        self.logger.level("UNK", no=10, color="<white>", icon="unknown")
        self.logger.level("CMD", no=25, color="<green><bold>", icon="command")
        if debug:
            self.logger.add(sink=sys.stdout, format="<b><e>{level}</e>: \
<e>{message}</e></b>",
                            colorize=True, level=10,
                            filter=debug_only)
        self.logger.add(sink=sys.stdout, format="<b>{level}: {message}</b>",
                        colorize=True, level=20,
                        filter=info_only)
        self.logger.add(sink=sys.stdout, format="<b><y>{level}</y>: \
<y>{message}</y></b>",
                        colorize=True, level=30,
                        filter=warning_only)
        self.logger.add(sink=sys.stdout, format="<b><g>{level}</g>: \
<g>{message}</g></b>",
                        colorize=True, level=25,
                        filter=success_only)
        self.logger.add(sink=sys.stdout, format="<b><g>{level}</g>: \
<g>{message}</g></b>",
                        colorize=True, level=25,
                        filter=command_only)
        self.logger.add(sink=sys.stdout, format="<b><r>{level}</r>: \
<r>{message}</r></b>",
                        colorize=True, level=40,
                        filter=error_only)
        self.logger.add(sink=sys.stdout, format="{message}",
                        colorize=True, level=10,
                        filter=unknown_only)


def build_compile_cmd(df):
    cmd = None
    if df.suffix == '.sv':
        cmd = 'xvlog -sv '
    elif df.suffix == '.v':
        cmd = 'xvlog '
    elif df.suffix == '.vhdl':
        cmd = 'xvhdl -2008 '
    cmd = cmd + str(df)
    return cmd


def parse(content, v):
    d_content = content.decode().split("\n")
    f_content = filter(lambda line: line != '', d_content)
    for line in f_content:
        label = None
        text = None
        if ':' in line:
            line_c = line.split(':', 1)
            label = line_c[0]
            text = line_c[1]
        if label == 'ERROR':
            logger.error(f"{text}")
        elif label == 'WARNING':
            logger.warning(f"{text}")
        elif label == 'INFO':
            logger.info(f"{text}")
        elif (v):
            logger.log('UNK', f"{text}")


def launch(cmd, v):
    logger.log("CMD", f"{cmd}")
    process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    parse(stdout, v)
    parse(stderr, v)
    rc = process.returncode
    if (rc != 0):
        logger.error(f"RC of {cmd} is {rc}")
    return rc


def get_defines(dic):
    cmd = ''
    for d in dic:
        cmd += '-d ' + d + '=' + str(dic[d]) + ' '
    return cmd


def unknown_only(record):
    return record["level"].name == "UNK"


def command_only(record):
    return record["level"].name == "CMD"


def info_only(record):
    return record["level"].name == "INFO"


def debug_only(record):
    return record["level"].name == "DEBUG"


def success_only(record):
    return record["level"].name == "SUCCESS"


def error_only(record):
    return record["level"].name == "ERROR"


def critical_only(record):
    return record["level"].name == "CRITICAL"


def warning_only(record):
    return record["level"].name == "WARNING"
