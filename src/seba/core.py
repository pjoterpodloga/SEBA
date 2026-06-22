import sys
import os
import shutil
import subprocess
import asyncio

from seba.logger import AsyncLogger
from seba.directory import SebaDirectoryTemplate
from seba.arguments import SebaArguments
from seba.setup import SebaSetupTool
from seba.parser import SebaParser
from seba.corners import SebaCorner

class Seba:
    @classmethod
    async def run(cls):

        await AsyncLogger.start("SEBA_$ts.log", to_console=True, directory="logs")

        SebaArguments(sys.argv)

        if SebaArguments.isSetupOn or SebaArguments.isSetupForceOn:
            SebaSetupTool.setup_repository(SebaArguments.repoPath, SebaArguments.isSetupForceOn)

        file_content = []
        with open(f"{SebaArguments.repoPath}/seba/{SebaDirectoryTemplate.seba_config_file.name}", "r") as f:
            file_content = f.readlines()

        seba_parser_config = SebaParser(file_content)
        seba_config = seba_parser_config.parse_seba_config()

        ### TODO: Write file reader from parsed config file

        with open(f"{SebaArguments.repoPath}/corners/{SebaDirectoryTemplate.corner_gen_file.name}", "r") as f:
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

        await cls.__terminate__()


    @classmethod
    async def __terminate__(cls, code=0):
        AsyncLogger.info("Script terminated")
        await asyncio.sleep(1)
        await AsyncLogger.stop()
        exit(code)

def run():
    asyncio.run(Seba.run())