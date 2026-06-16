from enum import Enum

from src.logger import *
from src.seba_config import *
from src.seba_corners import *
from src.seba_core import CornerGenerator, Corner, Token, TokenCorner, Parser

class SebaParser:

    def __init__(self, file_content):
        self.file_content = file_content
            
    def __prepare_seba_config__(self) -> list[list[Token]]:
        
        file_content_copy_merged = Parser.prepare_file(self.file_content)
        tokens = Parser.define_tokens(file_content_copy_merged)
        tokens = Parser.change_tokens(tokens, [Token.TOKEN_DICT["#"]], [Token.TOKEN_DICT["\n"]])
        tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT["#"]])
        tokens = Parser.group_tokens(tokens, [Token.DEFAULT_ID])
        tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT[" "], Token.TOKEN_DICT["\t"]])
        tokens = Parser.delete_after_tokens(tokens, [Token.TOKEN_DICT["\n"]], [Token.TOKEN_DICT["\\"]])
        tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT["\\"]])
        tokens = Parser.split_tokens(tokens, [Token.TOKEN_DICT["\n"]])

        return tokens
    
    def __prepare_corner_gen__(self) -> list[list[Token]]:
        
        file_content_copy_merged = Parser.prepare_file(self.file_content)
        tokens = Parser.define_tokens(file_content_copy_merged)
        tokens = Parser.change_tokens(tokens, [Token.TOKEN_DICT["#"]], [Token.TOKEN_DICT["\n"]])
        tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT["#"]])
        tokens = Parser.group_tokens(tokens, [Token.DEFAULT_ID, Token.TOKEN_DICT["="]])
        tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT[" "], Token.TOKEN_DICT["\t"], Token.TOKEN_DICT[","]])
        tokens = Parser.delete_after_tokens(tokens, [Token.TOKEN_DICT["\n"]], [Token.TOKEN_DICT["\\"]])
        tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT["\\"]])
        tokens = Parser.check_surrounding_token(tokens, [Token.TOKEN_DICT["="]], [Token.TOKEN_DICT["["], Token.TOKEN_DICT["]"]])
        tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT[","]])
        tokens = [TokenCorner.from_token(t) for t in tokens]
        tokens_list = Parser.split_tokens(tokens, [Token.TOKEN_DICT["\n"]])
        for it_tl in range(len(tokens_list)):
            tokens_list[it_tl] = Parser.bound_by_token(tokens_list[it_tl], [Token.TOKEN_DICT["["]], [Token.TOKEN_DICT["]"]])
            tokens_list[it_tl] = Parser.delete_tokens(tokens_list[it_tl], [Token.TOKEN_DICT["["], Token.TOKEN_DICT["]"]])
            group_idx = 0
            for it_t in range(len(tokens_list[it_tl])):
                tt = tokens_list[it_tl][it_t].type
                tv = tokens_list[it_tl][it_t].value

                if tt == Token.TOKEN_DICT["="] and tv != "==":
                    ### TODO: write proper message
                    raise Exception("some bs")

                tokens_list[it_tl][it_t].group = group_idx
                if tt == Token.TOKEN_DICT["="]:
                    group_idx = group_idx - 2
                group_idx = group_idx + 1
                
            tokens_list[it_tl] = Parser.delete_tokens(tokens_list[it_tl], [Token.TOKEN_DICT["="]])

        return tokens_list

    
    def parse_corner_gen(self) -> SebaCorner:
        
        tokens = self.__prepare_corner_gen__()

        pm_wrong_num_corner = lambda tl, fc:    f"Wrong number of arguments; row: {tl.line}, col: {tl.column}\n"\
                                                f"{fc[tl.line-1]}"\
                                                f"{"^"*(len(fc[tl.line-1])-1)}"
        
        pm_missing_corner = lambda tl, n, fc:   f"Missing corners: {n}; row: {tl.line}\n"\
                                                f"{fc[tl.line-1]}"\
                                                f"{"^"*(len(fc[tl.line-1])-1)}"
        
        pm_wrong_def_corner = lambda tl, fc:    f"Definition of corner after corner_gen is not allowed; row: {tl.line}, col: {tl.column}\n"\
                                                f"{fc[tl.line-1]}"\
                                                f"{"^"*(len(fc[tl.line-1])-1)}"

        corners_def = []                
        corners_gen = []

        corner_defenition_finish = False

        for it_tl, tl in enumerate(tokens):

            if len(tl) == 1:
                raise Exception(pm_wrong_num_corner(tl[0], self.file_content))
            
            cmd = [x.value for x in tl]

            if cmd[0] == "lib" or cmd[0] == "param":
                if len(cmd) != 2:
                    raise Exception(pm_wrong_num_corner(tl[0], self.file_content))
                
                if corner_defenition_finish:
                    raise Exception(pm_wrong_def_corner(tl[0], self.file_content))
                
                corners_def.append(Corner(cmd[0], cmd[1]))
                
            if cmd[0] == "corner_gen":
                if len(cmd)-1 != len(corners_def):
                    raise Exception(pm_wrong_num_corner(tl[0], self.file_content))
                
                values = [t.value for t in tl[1:]]
                grouping = [t.group for t in tl[1:]]

                corners_gen.append(CornerGenerator(corners_def, values, grouping))

        seba_corner = SebaCorner(corners_gen)

        return seba_corner
    

    def parse_seba_config(self) -> SebaConfig:

        tokens = self.__prepare_seba_config__()
        
        pm_wrong_cmd = lambda tl, fc:   f"Wrong number of arguments; row: {tl.line}, col: {tl.column}\n"\
                                            f"{fc[tl.line-1]}"\
                                            f"{"^"*(len(fc[tl.line-1])-1)}"

        seba_config = SebaConfig()

        for it_tl, tl in enumerate(tokens):

            if len(tl) == 1:
                raise Exception(pm_wrong_cmd(tl[0], self.file_content))

            cmd = [x.value for x in tl]

            if cmd[0].upper() == "NAME":
                if len(tl) != 2:
                    raise Exception(pm_wrong_cmd(tl[0], self.file_content))
                seba_config.name = cmd[1]

            if cmd[0].upper() == "CONTROL":
                if len(tl) != 2:
                    raise Exception(pm_wrong_cmd(tl[0], self.file_content))
                seba_config.control = cmd[1]

            if cmd[0].upper() == "TESTBENCH":
                if len(tl) != 2:
                    raise Exception(pm_wrong_cmd(tl[0], self.file_content))
                seba_config.tb = cmd[1]

            if cmd[0].upper() == "CORNERS":
                if len(tl) != 2:
                    raise Exception(pm_wrong_cmd(tl[0], self.file_content))
                seba_config.corners = cmd[1]

            if cmd[0].upper() == "SCRIPT":
                if len(tl) != 2:
                    raise Exception(pm_wrong_cmd(tl[0], self.file_content))
                seba_config.script = cmd[1]

            if cmd[0].upper() == "MEAS":
                if len(tl) != 2:
                    raise Exception(pm_wrong_cmd(tl[0], self.file_content))
                seba_config.meas = cmd[1]

            if cmd[0].upper() == "PLOT":
                if len(tl) != 2:
                    raise Exception(pm_wrong_cmd(tl[0], self.file_content))
                seba_config.plot = cmd[1]

            if cmd[0].upper() == "EXTRACTION":
                if len(tl) < 2:
                    raise Exception(pm_wrong_cmd(tl[0], self.file_content))
                seba_config.extraction = cmd[1:]

        return seba_config