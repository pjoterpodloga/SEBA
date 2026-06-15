import sys
import os
import shutil
import subprocess
import asyncio

from src.constants import *
from src.utils import *
from src.logger import *
from src.seba_directory import *
from src.seba_arguments import *
from src.seba_setup import *
from src.seba_parser import *
from src.seba_corners import *

class Seba:
    @classmethod
    async def run(cls):

        await AsyncLogger.start("SEBA_$ts.log", to_console=True, directory="logs")

        if(len(sys.argv) == 1):
            SebaArguments.show_help()
            await cls.terminate(1)

        argument_parser = SebaArguments()
        argument_parser.parse()

        if argument_parser.isShowHelpOn:
            argument_parser.show_help()

        if argument_parser.isDebugOn:
            argument_parser.print_config()

        if argument_parser.isSetupOn or argument_parser.isSetupForceOn:
            SebaSetupTool.setup_repository(argument_parser.repoPath, argument_parser.isSetupForceOn)

        file_content = []
        with open(f"{argument_parser.repoPath}/seba/{SebaDirectoryTemplate.seba_config_file.name}", "r") as f:
            file_content = f.readlines()

        seba_parser_config = SebaParser(file_content)
        seba_config = seba_parser_config.parse_seba_config()

        ### TODO: Write file reader from parsed config file

        with open(f"{argument_parser.repoPath}/corners/{SebaDirectoryTemplate.corner_gen_file.name}", "r") as f:
            file_content = f.readlines()

        seba_parser_corners = SebaParser(file_content)
        seba_corners = seba_parser_corners.parse_corner_gen()
        sc  = seba_corners.generate_spice_corners()
        cl  = seba_corners.generate_corner_list()

        try:
            for x in sc:
                print(x)
            for x in cl:
                print(x)
        except Exception as ex:
            AsyncLogger.error(ex)

        await cls.terminate()


    @classmethod
    async def terminate(cls, code=0):
        AsyncLogger.info("Script terminated")
        await asyncio.sleep(1)
        await AsyncLogger.stop()
        exit(code)