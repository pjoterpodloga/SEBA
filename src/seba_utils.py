import sys
import os
import shutil
import subprocess
import asyncio

from src.utils import *
from src.constants import *
from src.logger import *

gitignore_file_content =    "# Default SEBA .gitignore file\n\n"\
                            "tmp/\n"\
                            "logs/\n"\
                            "backup/\n"\
                            "pex/\n"

seba_config_file_content =  "# Example of configuration for SEBA file"\
                            ""

seba_config_file = DefaultFile("config.seba", seba_config_file_content)
gitignore_file = DefaultFile(".gitignore", gitignore_file_content)
seba_folder = FolderTree("seba", [seba_config_file])
spfiles_folder = FolderTree("spfiles", ["<control.spice>"])
tb_folder = FolderTree("tb", ["<testbench.spice>"])
circuit_folder = FolderTree("circuit", ["<circuit.sch>", "<circuit.sym>"])
layout_folder = FolderTree("layout", ["<layout.gds>"])
corners_folder = FolderTree("corners", ["<corner.gen>", "<corner.list>"])
pex_folder = FolderTree("pex", ["<circuit.pex.spice>"])
scripts_folder = FolderTree("scripts", ["<script.py>"])
reports_folder = FolderTree("reports", ["<index.html>"])
logs_folder = FolderTree("logs", ["<seba.log>"])
simulation_folder = FolderTree("simulations", ["sim_1_tb", "...", "sim_n_tb"])
layout_flatten_gds_folder = FolderTree("layout_flatten_gds", [])
layout_lvs_folder = FolderTree("layout_lvs", [])
layout_drc_folder = FolderTree("layout_drc", [])
pex_tmp_folder = FolderTree("pex_tmp", [])
tmp_folder = FolderTree("tmp", [simulation_folder, layout_flatten_gds_folder, layout_lvs_folder, layout_drc_folder, pex_tmp_folder])
backup_folder = FolderTree("backup", ["<backup.zip>"])
root_tree = FolderTree("<repo_name>", [seba_folder, spfiles_folder, tb_folder, circuit_folder,
                                       layout_folder, corners_folder, pex_folder, scripts_folder,
                                       reports_folder, logs_folder, tmp_folder, backup_folder,
                                       gitignore_file])

class SebaArguments:
    isDebugOn=False
    isShowHelpOn = False
    isSetupOn = False
    isSetupForceOn = False
    isShowGitInitOn = False
    repoPath = ""

    @classmethod
    def parse(cls):

        AsyncLogger.info(f"Parsing input arguments")

        it = 0

        while True:
            
            if it == len(sys.argv):
                break

            if it == 0:
                it = it + 1
                continue
            
            if sys.argv[it] == SebaInputArguments.s_help or sys.argv[it] == SebaInputArguments.l_help:
                cls.isShowHelpOn = True
                it = it + 1
                continue

            if sys.argv[it] == SebaInputArguments.s_setup or sys.argv[it] == SebaInputArguments.l_setup:
                cls.isSetupOn = True
                cls.repoPath = sys.argv[it+1]
                it = it + 2
                continue

            if sys.argv[it] == SebaInputArguments.l_setup_force:
                cls.isSetupForceOn = True
                cls.repoPath = sys.argv[it+1] 
                it = it + 2
                continue

            if sys.argv[it] == SebaInputArguments.s_debug or sys.argv[it] == SebaInputArguments.l_debug:
                cls.isDebugOn = True
                it = it + 1
                continue
    
    @classmethod
    def print_config(cls):
        AsyncLogger.debug(f"SEBA configuration:")
        AsyncLogger.debug(f"\tIS_SHOW_HELP_ON = {cls.isShowHelpOn}")
        AsyncLogger.debug(f"\tIS_SETUP_ON = {cls.isSetupOn}")
        AsyncLogger.debug(f"\tREPO_PATH = {cls.repoPath}")
        AsyncLogger.debug(f"\tIS_DEBUG_ON = {cls.isDebugOn}")

    @classmethod
    def show_help(cls):
        
        AsyncLogger.info(f"Help message for {TextFormat.bold("S")}imulation {TextFormat.bold("E")}nvironmet {TextFormat.bold("B")}uilding {TextFormat.bold("A")}ssitance script")
        AsyncLogger.info(f"")
        AsyncLogger.info(f"Input arguments:")
        AsyncLogger.info(f"\t{SebaInputArguments.m_help}")
        AsyncLogger.info(f"\t{SebaInputArguments.m_setup}")
        AsyncLogger.info(f"\t{SebaInputArguments.m_setup_force}")
        AsyncLogger.info(f"\t{SebaInputArguments.m_debug}")
        cls.__print_dir_template__()


    @classmethod
    def __print_dir_template__(cls):

        AsyncLogger.info(f"")
        AsyncLogger.info(f"SEBA directory setup template:")
        for rtl in root_tree.resolve_tree_list():
            AsyncLogger.info(rtl)
        AsyncLogger.info(f"")

class SebaSetupTool:
    pathExists = None
    repoExists = None

    @classmethod
    def check_if_repo_exist(cls, repo_path):

        if os.path.exists(repo_path):
            cls.pathExists = True

        if cls.pathExists and os.path.exists(repo_path+"/.git"):
            cls.repoExists = True
            AsyncLogger.error(f"Repository already exists.")
        elif cls.pathExists and not os.path.exists(repo_path+"/.git"):
            cls.repoExists = False
            AsyncLogger.warning(f"Path already exists but repository setup in there.")

        return cls.pathExists

    @classmethod
    def setup_repository(cls, repo_path, force=False):

        repoExists = cls.check_if_repo_exist(repo_path)

        if repoExists and not force:
            AsyncLogger.error(f"To remove existing path pass --setup_force <repo_path> argument.")
            return
        
        if not repoExists and not force:
            AsyncLogger.info(f"Setting up new repository: {repo_path}")

        if force:
            AsyncLogger.warning(f"Removing existing {repo_path} repository or path and replacing it.")
            shutil.rmtree(repo_path, ignore_errors=True)

        cls.__setup_new_directory__(repo_path)

    @classmethod
    def __setup_new_directory__(cls, repo_path):
        AsyncLogger.info(f"Setting up repository")
        subprocess.run(["mkdir", repo_path])

        subprocess.run(["git", "init", repo_path], stdout=subprocess.DEVNULL)
        SebaArguments.isShowGitInitOn = True

        dir_to_create = root_tree.resolve_tree()

        for dtc in dir_to_create:
            dtc_path = dtc.replace("<repo_name>", repo_path)
            subprocess.run(["mkdir", "-p", dtc_path])

        default_files_to_create = root_tree.resolve_default_files()

        for dftc in default_files_to_create:
            dftc_path = dftc[0].replace("<repo_name>", repo_path)
            dftc_content = dftc[1]
            with open(dftc_path, "w") as f:
                f.write(dftc_content)
            

class Seba:
    @classmethod
    async def run(cls):

        await AsyncLogger.start("tmp/SEBA.log", to_console=True)

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

        await cls.terminate()

    @classmethod
    async def terminate(cls, code=0):
        AsyncLogger.info("Script terminated")
        await asyncio.sleep(1)
        await AsyncLogger.stop()
        exit(code)