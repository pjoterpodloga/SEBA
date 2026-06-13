import os
import subprocess
import shutil

from src.constants import *
from src.logger import *
from src.seba_directory import *

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
        
        ### TODO: Add creating mock files for debug purpose
        ### TODO: Add git init basic routine for connecting remote repo