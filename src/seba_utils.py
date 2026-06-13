import sys
import os
import shutil
import subprocess
import asyncio

from src.utils import *
from src.constants import *
from src.logger import *

class SebaArguments:
    isDebugOn=False
    isShowHelpOn = False
    isSetupOn = False
    isSetupForceOn = False
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
        for rtl in SebaDirectoryTemplate.root_tree.resolve_tree_list():
            AsyncLogger.info(rtl)
        AsyncLogger.info(f"")
        for scfc in SebaDirectoryTemplate.seba_config_file_content.split("\n"):
            AsyncLogger.info(scfc)
        AsyncLogger.info(f"")
        for cgfc in SebaDirectoryTemplate.corner_gen_file_content.split("\n"):
            AsyncLogger.info(cgfc)
        AsyncLogger.info(f"")
        for pfc in SebaDirectoryTemplate.plot_file_content.split("\n"):
            AsyncLogger.info(pfc)
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

        dir_to_create = SebaDirectoryTemplate.root_tree.resolve_tree()

        for dtc in dir_to_create:
            dtc_path = dtc.replace("<repo_name>", repo_path)
            subprocess.run(["mkdir", "-p", dtc_path])

        default_files_to_create = SebaDirectoryTemplate.root_tree.resolve_default_files()

        for dftc in default_files_to_create:
            dftc_path = dftc[0].replace("<repo_name>", repo_path)
            dftc_content = dftc[1]
            with open(dftc_path, "w") as f:
                f.write(dftc_content)

class SebaCornerGeneration:

    class Corner:
        def __init__(self, corner_type, corner_name):
            self.type = corner_type
            self.name = corner_name

    class CornerGenerator:
        def __init__(self, corners, values, grouping):
            self.corners = corners
            self.values = values
            
            total_number_of_corners = 1
            current_group = -1

            for it, v in enumerate(self.values):
                if current_group == grouping[it]:
                    continue
                total_number_of_corners = total_number_of_corners * len(v)
                current_group = grouping[it]

            self.tnoc = total_number_of_corners

            self.resolve()


        def resolve(self, return_list=True, return_spice=True):
            index_list = [0]*len(self.corners)

            it_gen = 0
            current_group = -1

            while it_gen < self.tnoc:
                for it_c in range(self.corners-1, -1, -1):
                    pass
                
                
            return 

    @classmethod
    def get_corners_generators(cls, corner_gen):
        
        corner_gen_copy = corner_gen.copy()

        error_encountered = False
        
        for it_cgc in range(len(corner_gen_copy)):
            corner_gen_copy[it_cgc] = f"{it_cgc+1}$"+corner_gen_copy[it_cgc].split("#")[0]+"#"

        parsed_corner = []

        for it_cgc, cg in enumerate(corner_gen_copy):
            
            substring_start = -1
            substring_stop = -1

            substrings = []

            for it_ch, ch in enumerate(cg):

                is_delimiter = (ch == " ") or (ch == "\t") or (ch == "#") or (ch == "$")
                is_substring_start = not is_delimiter and substring_start == -1
                is_substring_stop = is_delimiter and substring_start != -1 and substring_stop == -1

                if is_substring_start:
                    substring_start = it_ch
                
                if is_substring_stop:
                    substring_stop = it_ch

                substring_found = substring_start != -1 and substring_stop != -1

                if substring_found:
                    substrings.append(cg[substring_start : substring_stop])
                    substring_start = -1
                    substring_stop = -1

            parsed_corner.append(substrings)
        
        found_lib_param = True
        
        corners = []

        for it_pc, pc in enumerate(parsed_corner):
            c_type = None
            c_name = None

            if len(pc) <= 1:
                continue

            if pc[1] == "lib" or pc[1] == "param":
                c_type = pc[1]
                found_lib_param = True
            elif found_lib_param:
                break
            else:
                AsyncLogger.error(f"Wrong placement or missing corner type in line {pc[0]}")
                error_encountered = True
            
            if c_type != None and len(pc) != 3:
                AsyncLogger.error(f"Wrong number of parameters after corner type in line {pc[0]}")
                error_encountered = True

            c_name = pc[2]

            corners.append(SebaCornerGeneration.Corner(c_type, c_name))

        found_corner_gen = False

        corner_generators = []
        it_pc = 0

        for it_pc, pc in enumerate(parsed_corner):
            
            pc_copy = pc.copy()

            for it_pc_split in range(len(pc_copy)-1, -1, -1):
                split = pc_copy[it_pc_split].split("==")
                if len(split) != 1:
                    pc_copy.insert(it_pc_split, split)

            if len(pc_copy) <= 1:
                continue

            if pc_copy[1] == "corner_gen":
                found_corner_gen = True
            elif found_corner_gen:
                break
            else:
                continue

            if len(pc_copy) - 2 != len(corners):
                AsyncLogger.error(f"Wrong number of corners in corner_gen in line {pc[0]}")
                error_encountered = True
                break

            values = []
            grouping = []
            it_g = 0

            for v in pc[2:]:
                corr_v = v.split("==")

                ref_l = len(corr_v[0].split(","))

                for cv in corr_v:
                    if len(cv.split(",")) != ref_l:
                        AsyncLogger.error(f"Wrong number of paired corners in line {pc[0]}")
                        error_encountered = True
                        break
                    grouping.append(it_g)
                    values.append(cv.split(","))

                it_g = it_g + 1

            corner_generators.append(SebaCornerGeneration.CornerGenerator(corners, values, grouping))

        return corner_generators

            
                
            

        






class Seba:
    @classmethod
    async def run(cls):

        await AsyncLogger.start("tmp/SEBA.log", to_console=True)

        SebaCornerGeneration.get_corners_generators(SebaDirectoryTemplate.corner_gen_file_content.split("\n"))

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