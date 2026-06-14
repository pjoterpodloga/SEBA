from enum import Enum

from src.logger import *

class SebaConfig:
    name = None
    control = None
    tb = None
    corners = None
    script = None
    plot = None
    meas = None
    extraction = None

    def __init__(self, name=None, control=None, tb=None, corners=None, 
                 script=None, plot=None, meas=None, extraction=None):
        SebaConfig.name = name
        SebaConfig.control = control
        SebaConfig.tb = tb
        SebaConfig.corners = corners
        SebaConfig.script = script
        SebaConfig.plot = plot
        SebaConfig.meas = meas
        SebaConfig.extraction = extraction

class SebaParser:

    class Token:
        COMMENT_CH  = "#"
        SPACE_CH    = " "
        TAB_CH      = "\t"
        INDEX_CH    = "$"
        EXTEND_CH   = "\\"
        CORR_CH     = "="
        LIST_BEG_CH = "["
        LIST_END_CH = "]"
        COMMA_CH    = ","
        ENDLINE_CH  = "\n"

        STRING_ID   = 1
        COMMENT_ID  = 2
        SPACE_ID    = 3
        TAB_ID      = 4
        INDEX_ID    = 5
        EXTEND_ID   = 6
        CORR_ID     = 7
        LIST_BEG_ID = 8
        LIST_END_ID = 9
        COMMA_ID    = 10
        ENDLINE_ID  = 11

        TOKEN_DICT = {
            COMMENT_CH  : COMMENT_ID,
            SPACE_CH    : SPACE_ID,
            TAB_CH      : TAB_ID,
            INDEX_CH    : INDEX_ID,
            EXTEND_CH   : EXTEND_ID,
            CORR_CH     : CORR_ID,
            LIST_BEG_CH : LIST_BEG_ID,
            LIST_END_CH : LIST_END_CH,
            COMMA_CH    : COMMA_ID,
            ENDLINE_CH  : ENDLINE_ID
        }

    class PreState(Enum):
        NONE        = 0
        INDEX       = 1
        CONT_INDEX  = 2
        COMMAND     = 3
        ARRAY       = 4
        COMMENT     = 5
        ENDLINE     = 6

    class CommandState(Enum):
        NONE        = 0
        NAME        = 1
        CONTROL     = 2
        TESTBENCH   = 3
        CORNERS     = 4
        SCRIPT      = 5
        MEAS        = 6
        PLOT        = 7
        EXTRACTION  = 8

    __filename__ = None
    __file_content__ = None
    
    __seba_name__ = None
    __control_file_name__ = None
    __testbench_file_name__ = None
    __corners_gen_file_name__ = None
    __script_file_name__ = None
    __meas_file_name__ = None
    __plot_file_name__ = None
    __extraction_names__ = None

    @classmethod
    def parse(cls, filename):
        cls.__filename__ = filename

        with open(cls.__filename__, "r") as f:
            cls.__file_content__ = f.readlines()

        ### TODO: extract parser to function
        ### TODO: copy and adjust parser to corner_gen file

        file_content_copy = cls.__file_content__.copy()
        file_content_copy.append("\n")

        for it_fcc in range(len(file_content_copy)):
            file_content_copy[it_fcc] = f"${it_fcc} " + file_content_copy[it_fcc]

        file_content_copy_merged = "".join(file_content_copy)

        token_dict = SebaParser.Token.TOKEN_DICT

        token_type = [0]*len(file_content_copy_merged)
        token_keys = token_dict.keys()

        for it_fccm, fccm in enumerate(file_content_copy_merged):
            if fccm in token_keys:
                token_type[it_fccm] = token_dict[fccm]
            else:
                token_type[it_fccm] = SebaParser.Token.STRING_ID

        extracted_value = []

        extract_start = -1
        extract_stop = -1

        ignore_endline = False
        index_extracted = False

        current_state = SebaParser.PreState.NONE
        next_state = SebaParser.PreState.NONE

        substrings_v = []
        substrings_t = []

        for it_tt, tt in enumerate(token_type):
            
            if tt == SebaParser.Token.INDEX_ID:
                if ignore_endline:
                    next_state = SebaParser.PreState.CONT_INDEX
                    ignore_endline = False
                else:
                    next_state = SebaParser.PreState.INDEX

            if tt == SebaParser.Token.STRING_ID:
                if extract_start == -1:
                    extract_start = it_tt
                    extract_stop = -1

                if index_extracted and current_state == SebaParser.PreState.INDEX:
                    next_state = SebaParser.PreState.COMMAND

            if tt == SebaParser.Token.SPACE_ID:
                extract_stop = it_tt

            if tt == SebaParser.Token.TAB_ID:
                extract_stop = it_tt

            if tt == SebaParser.Token.COMMENT_ID:
                next_state = SebaParser.PreState.COMMENT

            if tt == SebaParser.Token.EXTEND_ID:
                ignore_endline = True

            if tt == SebaParser.Token.ENDLINE_ID:
                if not ignore_endline:
                    next_state = SebaParser.PreState.ENDLINE
                    index_extracted = False
                    extract_stop = it_tt

            if extract_start != -1 and extract_stop != -1:
                substring = file_content_copy_merged[extract_start : extract_stop].replace("\n", "").replace("\\", "")
                substrings_v.append(substring)
                substrings_t.append(current_state.value)

                if next_state == SebaParser.PreState.ENDLINE:
                    substrings_v.append("")
                    substrings_t.append(next_state.value)

                if current_state == SebaParser.PreState.INDEX or current_state == SebaParser.PreState.CONT_INDEX:
                    index_extracted = True

                extract_start = -1
                extract_stop = -1

            current_state = next_state
            
        for it_ss in range(len(substrings_t)-1, -1, -1):
            is_comment = substrings_t[it_ss] == SebaParser.PreState.COMMENT.value
            is_endline = substrings_t[it_ss] == SebaParser.PreState.ENDLINE.value
            if is_comment or is_endline:
                substrings_t.pop(it_ss)
                substrings_v.pop(it_ss)

        extract_start = -1
        extract_stop = -1

        current_state = SebaParser.CommandState.NONE
        next_state = SebaParser.CommandState.NONE

        commands = []
        commands_t = []
        line_idx = -1

        for it_ss in range(len(substrings_t)):
            ssv = substrings_v[it_ss]
            sst = substrings_t[it_ss]

            if ssv == "NAME":
                next_state = SebaParser.CommandState.NAME
                extract_start = it_ss
                extract_stop = -1
            if ssv == "CONTROL":
                next_state = SebaParser.CommandState.CONTROL
                extract_start = it_ss
                extract_stop = -1
            if ssv == "TESTBENCH":
                next_state = SebaParser.CommandState.TESTBENCH
                extract_start = it_ss
                extract_stop = -1
            if ssv == "CORNERS":
                next_state = SebaParser.CommandState.CORNERS
                extract_start = it_ss
                extract_stop = -1
            if ssv == "SCRIPT":
                next_state = SebaParser.CommandState.SCRIPT
                extract_start = it_ss
                extract_stop = -1
            if ssv == "MEAS":
                next_state = SebaParser.CommandState.MEAS
                extract_start = it_ss
                extract_stop = -1
            if ssv == "PLOT":
                next_state = SebaParser.CommandState.PLOT
                extract_start = it_ss
                extract_stop = -1
            if ssv == "EXTRACTION":
                next_state = SebaParser.CommandState.EXTRACTION
                extract_start = it_ss
                extract_stop = -1
            if sst == SebaParser.PreState.INDEX.value:
                line_idx = ssv
                extract_stop = it_ss

            if extract_start != -1 and extract_stop != -1:
                cmd = [line_idx, next_state ,substrings_v[extract_start : extract_stop]]
                commands.append(cmd)

                extract_start = -1
                extract_stop = -1

            current_state = next_state

        for it_c in range(len(commands)):
            tmp = commands[it_c]

            line_idx = tmp[0]
            cmd_t = tmp[1]
            cmd_v = tmp[2]

            if cmd_t == SebaParser.CommandState.NAME:
                if len(cmd_v) != 2:
                    raise Exception(f"Wrong number of arguments in line {line_idx}")
                cls.__seba_name__ = cmd_v[1]

            if cmd_t == SebaParser.CommandState.CONTROL:
                if len(cmd_v) != 2:
                    raise Exception(f"Wrong number of arguments in line {line_idx}")
                cls.__control_file_name__ = cmd_v[1]

            if cmd_t == SebaParser.CommandState.TESTBENCH:
                if len(cmd_v) != 2:
                    raise Exception(f"Wrong number of arguments in line {line_idx}")
                cls.__testbench_file_name__ = cmd_v[1]

            if cmd_t == SebaParser.CommandState.CORNERS:
                if len(cmd_v) != 2:
                    raise Exception(f"Wrong number of arguments in line {line_idx}")
                cls.__corners_gen_file_name__ = cmd_v[1]

            if cmd_t == SebaParser.CommandState.SCRIPT:
                if len(cmd_v) != 2:
                    raise Exception(f"Wrong number of arguments in line {line_idx}")
                cls.__script_file_name__ = cmd_v[1]

            if cmd_t == SebaParser.CommandState.MEAS:
                if len(cmd_v) != 2:
                    raise Exception(f"Wrong number of arguments in line {line_idx}")
                cls.__meas_file_name__ = cmd_v[1]

            if cmd_t == SebaParser.CommandState.PLOT:
                if len(cmd_v) != 2:
                    raise Exception(f"Wrong number of arguments in line {line_idx}")
                cls.__plot_file_name__ = cmd_v[1]
                        
            if cmd_t == SebaParser.CommandState.EXTRACTION:
                if len(cmd_v) < 2:
                    raise Exception(f"Wrong number of arguments in line {line_idx}")
                cls.__extraction_names__ = cmd_v[1:]
        
        SebaConfig.name = cls.__seba_name__
        SebaConfig.control = cls.__control_file_name__
        SebaConfig.tb = cls.__testbench_file_name__
        SebaConfig.corners = cls.__corners_gen_file_name__
        SebaConfig.script = cls.__script_file_name__
        SebaConfig.meas = cls.__meas_file_name__
        SebaConfig.plot = cls.__plot_file_name__
        SebaConfig.extraction = cls.__extraction_names__

        return