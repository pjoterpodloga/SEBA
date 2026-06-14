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

        SebaArguments.parse()

        if SebaArguments.isShowHelpOn:
            SebaArguments.show_help()

        if SebaArguments.isDebugOn:
            SebaArguments.print_config()

        if SebaArguments.isSetupOn or SebaArguments.isSetupForceOn:
            SebaSetupTool.setup_repository(SebaArguments.repoPath, SebaArguments.isSetupForceOn)

        file_content = []
        with open(f"{SebaArguments.repoPath}/seba/{SebaDirectoryTemplate.seba_config_file.name}", "r") as f:
            file_content = f.readlines()

        SebaParser.parse_seba(file_content)
        
        ### TODO: Write file reader

        try:
            cgf = SebaDirectoryTemplate.corner_gen_file_content.split("\n")
            SebaCornerGeneration.set_corner_gen_file(cgf)
            sc  = SebaCornerGeneration.generate_spice_corners()
            cl  = SebaCornerGeneration.generate_corner_list()
        except Exception as ex:
            AsyncLogger.error(ex)

        await cls.terminate()


    @classmethod
    async def terminate(cls, code=0):
        AsyncLogger.info("Script terminated")
        await asyncio.sleep(1)
        await AsyncLogger.stop()
        exit(code)