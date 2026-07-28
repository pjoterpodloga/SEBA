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
from seba.variants import SebaVariant
from seba.extraction import SebaExtractionMap, SebaExtraction
from seba.assembler import SebaAssembler
from seba.simulate import SebaSimulate
from seba.result import SebaResult

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

            SebaSetupTool.setup_repository(SebaArguments)

        if SebaArguments.isCreateVenvOn:
            SebaSetupTool.create_venv_directory(SebaArguments)

        if SebaArguments.sebaFile != None:
            file_content = []
            with open(SebaArguments.sebaFile, "r") as f:
                file_content = f.readlines()

            seba_parser_config = SebaParser(None, file_content, SebaArguments)
            seba_config = seba_parser_config.parse_seba_config()

            os.chdir(seba_config.config_dir)

        if (SebaArguments.isBuildOn or SebaArguments.isBuildForceOn) and\
            SebaArguments.sebaFile != None:

            SebaSetupTool.prepare_sim_dir(seba_config, SebaArguments)

            seba_reader = SebaReader(seba_config)

            seba_parser_corners = SebaParser(seba_config, seba_reader.corners_file, SebaArguments)
            seba_corners = seba_parser_corners.parse_corner_gen()

            seba_parser_variants = SebaParser(seba_config, seba_reader.variants_file, SebaArguments)
            seba_variants = seba_parser_variants.parse_variant()

            seba_parser_netlist = SebaParser(seba_config, seba_reader.netlist_file, SebaArguments)
            seba_netlist = seba_parser_netlist.parse_netlist()

            seba_parser_control = SebaParser(seba_config, seba_reader.control_file, SebaArguments)
            seba_control = seba_parser_control.parse_control()

            seba_parser_measure = SebaParser(seba_config, seba_reader.measure_file, SebaArguments)
            seba_measure = seba_parser_measure.parse_measure()

            seba_extraction_list = SebaExtractionMap(seba_reader.extraction_files)

            seba_assembler = SebaAssembler(config=seba_config, 
                                            corners=seba_corners, variants=seba_variants,
                                            testbench=seba_netlist, control=seba_control,
                                            measure=seba_measure, script=seba_reader.script_file,
                                            extraction=seba_extraction_list)

            seba_assembler.write_all()

        if SebaArguments.isSimulateOn and SebaArguments.sebaFile != None:
            os.chdir(seba_config.sim_dir)
            seba_simulate = SebaSimulate(seba_config)
            os.chdir(seba_config.config_dir)

        if SebaArguments.isResultGenOn and SebaArguments.sebaFile != None:
            seba_result = SebaResult(seba_config)
            seba_result.generate_results()

        cls.__terminate__()


    @classmethod
    def __terminate__(cls, code=0):
        AsyncLogger.info("Script terminated")
        AsyncLogger.stop()
        exit(code)

def run():
    Seba.run()