from seba.constants import SebaInputArguments
from seba.logger import AsyncLogger
from seba.directory import SebaDirectoryTemplate
from seba.utils import UnknownArgumentError, MissingArgumentError
from seba.utils import TextFormat

class SebaArguments:

    isDebugOn=False
    isShowHelpOn = False
    isSetupOn = False
    isSetupForceOn = False
    repoPath = ""
    args = None

    def __init__(self, args: list[str]):
        type(self).args = args
        type(self).__parse__()

        if type(self).isDebugOn:
            type(self).print_config()

        if type(self).isShowHelpOn or len(type(self).args) == 1:
            type(self).show_help()

    @classmethod
    def __parse__(cls):

        AsyncLogger.info(f"Parsing input arguments")

        it = 0

        while True:
            
            if it == len(cls.args):
                break

            if it == 0:
                it = it + 1
                continue
            
            if cls.args[it] == SebaInputArguments.s_help or cls.args[it] == SebaInputArguments.l_help:
                cls.isShowHelpOn = True
                it = it + 1
                break

            if cls.args[it] == SebaInputArguments.s_setup or cls.args[it] == SebaInputArguments.l_setup:
                cls.isSetupOn = True
                if len(cls.args)-1 == it:
                    raise MissingArgumentError(f"Missing argument for {cls.args[it]}")
                cls.repoPath = cls.args[it+1]
                it = it + 2
                continue

            if cls.args[it] == SebaInputArguments.l_setup_force:
                cls.isSetupForceOn = True
                if len(cls.args)-1 == it:
                    raise MissingArgumentError(f"Missing argument for {cls.args[it]}")
                cls.repoPath = cls.args[it+1]
                it = it + 2
                continue

            if cls.args[it] == SebaInputArguments.s_debug or cls.args[it] == SebaInputArguments.l_debug:
                cls.isDebugOn = True
                it = it + 1
                continue

            raise UnknownArgumentError(f"Unknown argument: {cls.args[it]}")
    
    @classmethod
    def print_config(cls):
        AsyncLogger.debug(f"SEBA configuration:")
        AsyncLogger.debug(f"IS_SHOW_HELP_ON = {cls.isShowHelpOn}")
        AsyncLogger.debug(f"IS_SETUP_ON = {cls.isSetupOn}")
        AsyncLogger.debug(f"REPO_PATH = {cls.repoPath}")
        AsyncLogger.debug(f"IS_DEBUG_ON = {cls.isDebugOn}")

    @classmethod
    def show_help(cls):
        
        AsyncLogger.info(f"Help message for {TextFormat.bold("S")}imulation {TextFormat.bold("E")}nvironmet {TextFormat.bold("B")}uilding {TextFormat.bold("A")}ssitance script")
        AsyncLogger.info(f"")
        AsyncLogger.info(f"Input arguments:")
        AsyncLogger.info(f"{SebaInputArguments.m_help}")
        AsyncLogger.info(f"{SebaInputArguments.m_setup}")
        AsyncLogger.info(f"{SebaInputArguments.m_setup_force}")
        AsyncLogger.info(f"{SebaInputArguments.m_debug}")
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
