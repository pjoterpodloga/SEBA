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

class Seba:
    @classmethod
    async def run(cls):

        await AsyncLogger.start("SEBA_$ts.log", to_console=True, directory="logs")

        SebaArguments(sys.argv)

        if SebaArguments.isSetupOn or SebaArguments.isSetupForceOn:
            SebaSetupTool.setup_repository(SebaArguments.repoPath, SebaArguments.isSetupForceOn)
            if not DEBUG:
                await cls.__terminate__()

        debug_repo_path = None

        file_content = []
        if DEBUG:
            SebaArguments.repoPath = "tmp/test_repo"
            debug_repo_path = SebaArguments.repoPath+"/"+SebaDirectoryTemplate.config_folder.name
            SebaSetupTool.setup_repository(SebaArguments.repoPath, SebaArguments.isSetupForceOn)
            os.chdir(debug_repo_path)
            AsyncLogger.debug(f"Root direcotry changed to: \"{debug_repo_path}\"")

            with open(f"config.debug.seba", "r") as f:
                file_content = f.readlines()
        else:
            with open(SebaArguments.sebaFile, "r") as f:
                file_content = f.readlines()
            

        seba_parser_config = SebaParser(file_content)
        seba_config = seba_parser_config.parse_seba_config()
        seba_reader = SebaReader(seba_config)

        seba_parser_corners = SebaParser(seba_reader.corners_file)
        seba_corners = seba_parser_corners.parse_corner_gen()

        seba_parser_testbench = SebaParser(seba_reader.testbench_file)
        seba_testbench = seba_parser_testbench.parse_testbench()

        for x in seba_testbench.get_spice_lines():
            print(x)

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