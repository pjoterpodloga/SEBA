import sys
import os
import shutil
import subprocess

from src.utils import *
from src.constants import *

class Seba:
    @classmethod
    def run():
        pass

seba_folder = FolderTree("seba", ["config", "<seba_files.seba>"])
spfiles_folder = FolderTree("spfiles", ["<control.spice>"])
tb_folder = FolderTree("tb", ["<testbench.spice>"])
circuit_folder = FolderTree("circuit", ["<circuit.sch>", "<circuit.sym>"])
layout_folder = FolderTree("layout", ["<layout.gds>"])
corners_folder = FolderTree("corners", ["<corner.gen>", "<corner.list>"])
pex_folder = FolderTree("pex", ["<circuit.pex.spice>"])
scripts_folder = FolderTree("scripts", ["<script.py>"])
reports_folder = FolderTree("reports", ["<index.html>"])
logs_folder = FolderTree("logs", ["<seba.log>"])
tmp_folder = FolderTree("tmp", ["<layout.flatten.gds>", "<layout.lvs>", "<layout.drc>", "<pex.tmp>"])
backup_folder = FolderTree("backup", ["<backup.zip>"])
root_tree = FolderTree("<repo_name>", [seba_folder, spfiles_folder, tb_folder, circuit_folder,
                                       layout_folder, corners_folder, pex_folder, scripts_folder,
                                       reports_folder, logs_folder, tmp_folder, backup_folder])

class SebaArguments:
    isDebug=DEBUG
    isShowHelpOn = False
    isSetupOn = False
    isSetupForceOn = False
    repoPath = ""

    @classmethod
    def parse(cls):

        print(f"Parsing input arguments")

        for it, arg in enumerate(sys.argv):
            if it == 0:
                continue
            
            if arg == SebaInputArguments.s_help or arg == SebaInputArguments.l_help:
                cls.isShowHelpOn = True

            if arg == SebaInputArguments.s_setup or arg == SebaInputArguments.l_setup:
                cls.isSetupOn = True
                cls.repoPath = sys.argv[it+1]

            if arg == SebaInputArguments.l_setup_force:
                cls.isSetupForceOn = True
                cls.repoPath = True
    
    @classmethod
    def print_config(cls):
        print(f"")
        print(f"SEBA configuration:")
        print(f"\tIS_DEBUG = {cls.isDebug}")
        print(f"\tIS_SHOW_HELP_ON = {cls.isShowHelpOn}")
        print(f"\tIS_SETUP_ON = {cls.isSetupOn}")
        print(f"\tREPO_PATH = {cls.repoPath}")
        print(f"")

    @classmethod
    def show_help(cls, force=False):
        if cls.isShowHelpOn or force:
            cls.__show_help__()

    @classmethod
    def __show_help__(cls):
        
        print(f"")
        print(f"Help message for {TextFormat.bold("S")}imulation {TextFormat.bold("E")}nvironmet {TextFormat.bold("B")}uilder {TextFormat.bold("A")}ssitance script")
        print(f"")
        print(f"Arguments:")
        print(f"\t{SebaInputArguments.m_help}")
        print(f"\t{SebaInputArguments.m_setup}")
        print(f"\t{SebaInputArguments.m_setup_force}")
        print(f"")
        cls.__print_dir_template__()
        print(f"")


    @classmethod
    def __print_dir_template__(cls):

        print(f"")
        print(f"SEBA directory setup template:")
        print(root_tree.resolve_tree_string())
        print(f"")

class SebaSetupTool:
    pathExists = None
    repoExists = None

    @classmethod
    def check_if_repo_exist(cls, repo_path):

        if os.path.exists(repo_path):
            cls.pathExists = True

        if cls.pathExists and os.path.exists(repo_path+"/.git"):
            cls.repoExists = True
            print(f"Repository already exists.")
        elif cls.pathExists and not os.path.exists(repo_path+"/.git"):
            cls.repoExists = False
            print(f"Path already exists but repository setup in there.")

        return cls.pathExists

    @classmethod
    def setup_repository(cls, repo_path, force=False):

        repoExists = cls.check_if_repo_exist(repo_path)

        if repoExists and not force:
            print(f"To remove existing path pass --setup_force <repo_path> argument.")
            return
        
        if not repoExists and not force:
            print(f"Setting up new repository: {repo_path}")

        if force:
            print(f"Removing existing {repo_path} repository or path and replacing it.")
            shutil.rmtree(repo_path, ignore_errors=True)

        cls.__setup_new_directory__(repo_path)

    @classmethod
    def __setup_new_directory__(cls, repo_path):
        print(f"Setting up repository")
        subprocess.run(["mkdir", repo_path])

        subprocess.run(["git", "init", repo_path])

        dir_to_create = root_tree.resolve_tree()

        for dtc in dir_to_create:
            dtc_path = dtc.replace("<repo_name>", repo_path)
            os.mkdir(dtc_path)
            subprocess.run(["touch", f"{dtc_path}/__placeholder__"])

    