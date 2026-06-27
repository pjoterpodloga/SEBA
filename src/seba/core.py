import sys
import os
import shutil
import subprocess
import asyncio

from seba.constants import DEBUG
from seba.logger import AsyncLogger
from seba.directory import SebaDirectoryTemplate
from seba.arguments import SebaArguments
from seba.setup import SebaSetupTool
from seba.parser import SebaParser
from seba.reader import SebaReader
from seba.corners import SebaCorner
from seba.assembler import SebaAssembler
from seba.simulate import SebaSimulate

class Seba:
    @classmethod
    def run(cls):

        AsyncLogger.start("SEBA_$ts.log", to_console=True, directory="logs")

        SebaArguments(sys.argv)

        if SebaArguments.isShowHelpOn:
            cls.__terminate__()

        if SebaArguments.isSetupOn or\
            SebaArguments.isSetupForceOn or\
            SebaArguments.isSetupDebugOn:

            SebaSetupTool.setup_repository(
                SebaArguments.repoPath, 
                SebaArguments.isSetupForceOn or SebaArguments.isSetupDebugOn, 
                SebaArguments.isCreateDebugFilesOn or SebaArguments.isSetupDebugOn)

        if SebaArguments.sebaFile != None:
            file_content = []
            with open(SebaArguments.sebaFile, "r") as f:
                file_content = f.readlines()

            seba_parser_config = SebaParser(None, file_content)
            seba_config = seba_parser_config.parse_seba_config()

            os.chdir(seba_config.config_dir)

        if (SebaArguments.isBuildOn or SebaArguments.isBuildForceOn) and\
            SebaArguments.sebaFile != None:

            SebaSetupTool.prepare_sim_dir(seba_config, SebaArguments.isBuildForceOn)

            seba_reader = SebaReader(seba_config)

            seba_parser_corners = SebaParser(seba_config,seba_reader.corners_file)
            seba_corners = seba_parser_corners.parse_corner_gen()

            seba_parser_testbench = SebaParser(seba_config,seba_reader.testbench_file)
            seba_testbench = seba_parser_testbench.parse_testbench()

            seba_parser_control = SebaParser(seba_config,seba_reader.control_file)
            seba_control = seba_parser_control.parse_control()

            seba_assembler = SebaAssembler(seba_config, seba_corners, 
                                           seba_testbench, seba_control)

        if SebaArguments.isSimulateOn and SebaArguments.sebaFile != None:
            os.chdir(seba_config.sim_dir)
            seba_simulate = SebaSimulate(seba_config)
            os.chdir(seba_config.config_dir)

        cls.__terminate__()


    @classmethod
    def __terminate__(cls, code=0):
        AsyncLogger.info("Script terminated")
        AsyncLogger.stop()
        exit(code)

def run():
    Seba.run()