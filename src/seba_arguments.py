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

            ### TODO: Add handling unknown argument
    
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
        for gfc in SebaDirectoryTemplate.gitignore_file_content.split("\n"):
            AsyncLogger.info(gfc)
        AsyncLogger.info(f"")
