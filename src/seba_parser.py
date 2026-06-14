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

class Token:
    DEFAULT_ID = 1

    SEARCH_VALUES = [" ", "\t", "\\", "#", "=", "[", "]", ",", "\n"]

    TOKEN_DICT = {x: i + 2 for i, x in enumerate(SEARCH_VALUES)}

    def __init__(self, type=None, value=None, line=None, column=None):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

class SebaParser:

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
    def __prepare_file__(cls, file_content: list[str]) -> str:
        file_content_copy = cls.__file_content__.copy()
        file_content_copy.append("\n")

        file_content_copy_merged = "".join(file_content_copy)

        return file_content_copy_merged

    @classmethod
    def __define_tokens_type__(cls, file_content: str) -> list[Token]:
        token_dict = Token.TOKEN_DICT

        token = [Token(0)]*len(file_content)
        token_keys = token_dict.keys()

        row = 1
        col = 1

        for it_fc, fc in enumerate(file_content):
            if fc in token_keys:
                token[it_fc] = Token(token_dict[fc], fc, row, col)
            else:
                token[it_fc] = Token(Token.DEFAULT_ID, fc, row, col)

            col = col + 1

            if fc == "\n":
                row = row + 1
                col = 1

        return token

    @classmethod
    def __change_token_type__(cls, tokens: list[Token], target: list[int], until: list[int]) -> list[Token]:

        if (target == None):
            raise Exception("\"Target\" token is \"None\"")
        if (type(target) != list):
            raise Exception("\"Tagert\" token is not \"list()\"")
        
        if (until == None):
            raise Exception("\"Until\" token is \"None\"")
        if (type(until) != list):
            raise Exception("\"Until\" token is not \"list()\"")

        current_target = 0
        t_found = False

        for it_t, t in enumerate(tokens):
            
            tt = t.type

            if tt in target:
                current_target = tt
                t_found = True
                continue
            
            if tt in until:
                current_target = 0
                t_found = False
                continue
            
            if t_found:
                tokens[it_t].type = current_target

        return tokens

    @classmethod
    def __delete_token_type__(cls, tokens: list[Token], target: list[int]) -> list[Token]:

        for it_t in range(len(tokens)-1, -1, -1):
            tt = tokens[it_t].type

            if tt in target:
                tokens.pop(it_t)

        return tokens
    
    @classmethod
    def __group_token_type__(cls, tokens: list[Token], target: list[int]) -> list[Token]:
        
        found_target = False
        current_target = -1

        grouped_value = ""

        grouped_token = Token()

        poped_token = Token()

        for it_t in range(len(tokens)-1, -1, -1):
            
            tt = tokens[it_t].type
            tv = tokens[it_t].value

            if tt != current_target and found_target:
                grouped_token = poped_token
                grouped_token.value = grouped_value
                tokens.insert(it_t+1, grouped_token)
                found_target = False
                continue

            if tt in target and not found_target:
                grouped_value = ""
                current_target = tt
                found_target = True

            if found_target:
                grouped_value = tv + grouped_value
                poped_token = tokens.pop(it_t)
        
        return tokens
    
    @classmethod
    def __split_tokens__(cls, tokens: list[Token], target: int) -> list[list[Token]]:
        
        result = []
        tmp_group = []
        
        for t in tokens:
            tt = t.type

            if tt in target and len(tmp_group) == 0:
                continue

            if tt in target:
                result.append(tmp_group)
                tmp_group = []
                continue

            tmp_group.append(t)

        return result

    @classmethod
    def __delete_after_token_type__(cls, tokens: list[Token], target: list[int], until: list[int]) -> list[Token]:

        target_found = False
        last_target_it = -1

        for it_t in range(len(tokens)-1, -1, -1):
            tt = tokens[it_t].type

            if tt in until and target_found:

                for it_d in range(last_target_it, it_t-1, -1):
                    tokens.pop(it_d)

                target_found = False
                
            if tt in target:
                target_found = True
                last_target_it = it_t

        return tokens

    @classmethod
    def __prepare_seba_tokens__(cls, file_content: list[str]):
        
        file_content_copy_merged = cls.__prepare_file__(file_content)
        tokens = cls.__define_tokens_type__(file_content_copy_merged)
        tokens = cls.__change_token_type__(tokens, [Token.TOKEN_DICT["#"]], [Token.TOKEN_DICT["\n"]])
        tokens = cls.__delete_token_type__(tokens, [Token.TOKEN_DICT["#"]])
        tokens = cls.__group_token_type__(tokens, [Token.DEFAULT_ID])
        tokens = cls.__delete_token_type__(tokens, [Token.TOKEN_DICT[" "], Token.TOKEN_DICT["\t"]])
        tokens = cls.__delete_after_token_type__(tokens, [Token.TOKEN_DICT["\n"]], [Token.TOKEN_DICT["\\"]])
        tokens = cls.__split_tokens__(tokens, [Token.TOKEN_DICT["\n"]])

        return tokens
    
    @classmethod
    def parse_corner_gen(cls, file_content: list[str]):
        pass

    @classmethod
    def parse_seba(cls, file_content: list[str]):

        cls.__file_content__ = file_content.copy()

        ### TODO: copy and adjust parser to corner_gen file

        tokens = cls.__prepare_seba_tokens__(cls.__file_content__)
        
        pm_too_short_cmd = lambda tl, fc:   f"Wrong number of arguments in row: {tl.line}, col: {tl.column}\n"\
                                            f"{fc[tl.line-1]}"\
                                            f"{"^"*(len(fc[tl.line-1])-1)}"

        for it_tl, tl in enumerate(tokens):

            if len(tl) == 1:
                raise Exception(pm_too_short_cmd(tl[0], file_content))

            cmd = [x.value for x in tl]

            if cmd[0].upper() == "NAME":
                if len(tl) != 2:
                    raise Exception(pm_too_short_cmd(tl[0], file_content))
                cls.__seba_name__ = cmd[1]

            if cmd[0].upper() == "CONTROL":
                if len(tl) != 2:
                    raise Exception(pm_too_short_cmd(tl[0], file_content))
                cls.__control_file_name__ = cmd[1]

            if cmd[0].upper() == "TESTBENCH":
                if len(tl) != 2:
                    raise Exception(pm_too_short_cmd(tl[0], file_content))
                cls.__testbench_file_name__ = cmd[1]

            if cmd[0].upper() == "CORNERS":
                if len(tl) != 2:
                    raise Exception(pm_too_short_cmd(tl[0], file_content))
                cls.__corners_gen_file_name__ = cmd[1]

            if cmd[0].upper() == "SCRIPT":
                if len(tl) != 2:
                    raise Exception(pm_too_short_cmd(tl[0], file_content))
                cls.__script_file_name__ = cmd[1]

            if cmd[0].upper() == "MEAS":
                if len(tl) != 2:
                    raise Exception(pm_too_short_cmd(tl[0], file_content))
                cls.__meas_file_name__ = cmd[1]

            if cmd[0].upper() == "PLOT":
                if len(tl) != 2:
                    raise Exception(pm_too_short_cmd(tl[0], file_content))
                cls.__plot_file_name__ = cmd[1]

            if cmd[0].upper() == "EXTRACTION":
                if len(tl) < 2:
                    raise Exception(pm_too_short_cmd(tl[0], file_content))
                cls.__extraction_names__ = cmd[1:]
                

        SebaConfig.name = cls.__seba_name__
        SebaConfig.control = cls.__control_file_name__
        SebaConfig.tb = cls.__testbench_file_name__
        SebaConfig.corners = cls.__corners_gen_file_name__
        SebaConfig.script = cls.__script_file_name__
        SebaConfig.meas = cls.__meas_file_name__
        SebaConfig.plot = cls.__plot_file_name__
        SebaConfig.extraction = cls.__extraction_names__

        return