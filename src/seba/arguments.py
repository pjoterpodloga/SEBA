from seba.constants import SebaInputArguments
from seba.logger import AsyncLogger
from seba.directory import SebaDirectoryTemplate
from seba.utils import UnknownArgumentError, MissingArgumentError
from seba.utils import TextFormat

class SebaArguments:

    def __init__(self, args: list[str]):
        self.args = args

        self.isDebugOn=False
        self.isShowHelpOn = False
        self.isSetupOn = False
        self.isSetupForceOn = False
        self.repoPath = ""

    def parse(self):

        AsyncLogger.info(f"Parsing input arguments")

        it = 0

        while True:
            
            if it == len(self.args):
                break

            if it == 0:
                it = it + 1
                continue
            
            if self.args[it] == SebaInputArguments.s_help or self.args[it] == SebaInputArguments.l_help:
                self.isShowHelpOn = True
                it = it + 1
                break

            if self.args[it] == SebaInputArguments.s_setup or self.args[it] == SebaInputArguments.l_setup:
                self.isSetupOn = True
                if len(self.args)-1 == it:
                    raise MissingArgumentError(f"Missing argument for {self.args[it]}")
                self.repoPath = self.args[it+1]
                it = it + 2
                continue

            if self.args[it] == SebaInputArguments.l_setup_force:
                self.isSetupForceOn = True
                if len(self.args)-1 == it:
                    raise MissingArgumentError(f"Missing argument for {self.args[it]}")
                self.repoPath = self.args[it+1]
                it = it + 2
                continue

            if self.args[it] == SebaInputArguments.s_debug or self.args[it] == SebaInputArguments.l_debug:
                self.isDebugOn = True
                it = it + 1
                continue

            raise UnknownArgumentError(f"Unknown argument: {self.args[it]}")
    
    def print_config(self):
        AsyncLogger.debug(f"SEBA configuration:")
        AsyncLogger.debug(f"\tIS_SHOW_HELP_ON = {self.isShowHelpOn}")
        AsyncLogger.debug(f"\tIS_SETUP_ON = {self.isSetupOn}")
        AsyncLogger.debug(f"\tREPO_PATH = {self.repoPath}")
        AsyncLogger.debug(f"\tIS_DEBUG_ON = {self.isDebugOn}")

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
        for pfc in SebaDirectoryTemplate.meas_file_content.split("\n"):
            AsyncLogger.info(pfc)
        AsyncLogger.info(f"")
        for gfc in SebaDirectoryTemplate.gitignore_file_content.split("\n"):
            AsyncLogger.info(gfc)
        AsyncLogger.info(f"")
