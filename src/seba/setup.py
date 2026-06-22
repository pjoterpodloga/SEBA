import os
import subprocess
import shutil

from seba.constants import *
from seba.logger import *
from seba.directory import *

class SebaSetupTool:
    pathExists = None
    repoExists = None

    @classmethod
    def check_if_repo_exists(cls, repo_path):

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
    def check_if_config_exists(cls):

        if os.path.isfile(".seba"):
            pass

    @classmethod
    def setup_repository(cls, repo_path, force=False):

        repoExists = cls.check_if_repo_exists(repo_path)

        if repoExists and not force:
            AsyncLogger.error(f"To remove existing path pass --setup_force <repo_path> argument.")
            return
        
        if not repoExists and not force:
            AsyncLogger.info(f"Setting up new repository: {repo_path}")

        if repoExists and force:
            AsyncLogger.warning(f"Removing existing {repo_path} repository or path and replacing it.")
            shutil.rmtree(repo_path, ignore_errors=True)

        cls.__setup_new_directory__(repo_path)

    @classmethod
    def __setup_new_directory__(cls, repo_path):
        AsyncLogger.info(f"Setting up repository")
        subprocess.run(["mkdir", "-p", repo_path])

        subprocess.run(["git", "init", repo_path], stdout=subprocess.DEVNULL)

        dir_to_create = SebaDirectoryTemplate.root_tree.resolve_tree()

        for dtc in dir_to_create:
            dtc_path = dtc.replace("<repo_name>", repo_path)
            subprocess.run(["mkdir", "-p", dtc_path])

        default_files_to_create = SebaDirectoryTemplate.root_tree.resolve_default_files(return_placeholders=True)

        for dftc in default_files_to_create:
            dftc_path = dftc[0].replace("<repo_name>", repo_path)
            dftc_content = dftc[1]
            with open(dftc_path, "w") as f:
                f.write(dftc_content)


        ### TODO: Resolve searching directories from default dir
        ### TODO: Add creating mock files for debug purpose
        if DEBUG:
            AsyncLogger.debug("Creating mock files.")
            with open(repo_path+"/config/"+"config.debug.seba", "w") as f:
                f.write("# Mock SEBA config file\n")
                f.write("NAME\t\tdebug_tb\n")
                f.write("CONTROL\t\tcontrol.debug.spice\n")
                f.write("TESTBENCH\tdebug_tb.debug.spice\n")
                f.write("CORNERS\t\tcorner.debug.gen\n")
                f.write("SCRIPT\t\tscript.debug.py\n")
                f.write("MEAS\t\tmeasure.debug.meas\n")
                f.write("PLOT\t\tplot.debug.plt\n")

            with open(repo_path+"/control/"+"control.debug.spice", "w") as f:
                f.write("* Title: Debug mock control file\n")
                f.write(".control\n")
                f.write("run\n")
                f.write("save all\n")
                f.write("set filetype=ascii\n")
                f.write("write debug_tb.raw all\n")
                f.write(".endc\n")
            
            with open(repo_path+"/testbench/"+"debug_tb.debug.spice", "w") as f:
                f.write("* Title: Debug mock testbench file\n")
                f.write("V1 net1 0 1\n")
                f.write("R1 net1 0 'xres'\n")
                f.write(".param xres1=1\n")
                f.write(".param xres2=1\n")
                f.write(".dc v1 0 1 0.01\n")
                f.write(".end\n")

            with open(repo_path+"/corners/"+"corner.debug.gen", "w") as f:
                f.write("# Mock corner_gen file\n")
                f.write("param xres1\n")
                f.write("param xres2\n")
                f.write("corner_gen [1, 2, 3, 4, 5] [1, 2, 3, 4, 5]\n")

            ### TODO: Add empty debug files
            with open(repo_path+"/scripts/"+"script.debug.py", "w") as f:
                f.write("# Mock python script file\n")

            with open(repo_path+"/result_gen/"+"plot.debug.plt", "w") as f:
                f.write("# Mock plot file\n")

            with open(repo_path+"/result_gen/"+"measure.debug.meas", "w") as f:
                f.write("# Mock measure file\n")

            with open(repo_path+"/pex/"+"debug.debug.pex.spice", "w") as f:
                f.write("* Title: Debug mock pex spice file\n")


            

        ### TODO: Add git init basic routine for connecting remote repo