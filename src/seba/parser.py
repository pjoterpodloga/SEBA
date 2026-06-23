from enum import Enum

from seba.constants import *
from seba.logger import *
from seba.arguments import *
from seba.config import *
from seba.corners import *
from seba.spice import SebaSpice
from seba.utils import CornerGenerator, Corner, Token, TokenCorner, Parser
from seba.utils import WrongNumberConfigCommands, UnknownConfigCommand, MissingNameConfig
from seba.utils import MissingCorner, DefinitionAfterCornerGen, WrongCornerDefinition
from seba.utils import EmptyCornerArray, MissingCornerValue, UnknownCornerCommand
from seba.utils import CornerDuplication

class SebaParser:

    def __init__(self, file_content: list[str]):

        if type(file_content) == str:
            self.file_content = [f"{fc}\n" for fc in file_content.split("\n")]
        else:
            self.file_content = file_content
            
    def __prepare_seba_config__(self) -> list[list[Token]]:
        
        file_content_copy_merged = Parser.prepare_file(self.file_content)
        tokens = Parser.define_tokens(file_content_copy_merged)
        tokens = Parser.change_tokens(tokens, [Token.TOKEN_DICT["#"]], [Token.TOKEN_DICT["\n"]])
        tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT["#"]])
        tokens = Parser.alter_tokens(tokens, [Token.TOKEN_DICT["."]], Token.DEFAULT_ID)
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

        pm_corr_wrong_indicator = lambda t, fc:\
            f"Wrong correlation indicator; row{t.line}, col:{t.column}\n"\
            f"{fc[t.line-1]}"\
            f"{"-"*(t.column - 1)}^"

        for it_tl in range(len(tokens_list)):
            tokens_list[it_tl] = Parser.bound_by_token(tokens_list[it_tl], [Token.TOKEN_DICT["["]], [Token.TOKEN_DICT["]"]])
            tokens_list[it_tl] = Parser.delete_tokens(tokens_list[it_tl], [Token.TOKEN_DICT["["], Token.TOKEN_DICT["]"]])
            group_idx = 0
            for it_t in range(len(tokens_list[it_tl])):
                tt = tokens_list[it_tl][it_t].type
                tv = tokens_list[it_tl][it_t].value

                if tt == Token.TOKEN_DICT["="] and tv != "==":
                    raise Exception(pm_corr_wrong_indicator(tokens_list[it_tl][it_t], self.file_content))

                tokens_list[it_tl][it_t].group = group_idx
                if tt == Token.TOKEN_DICT["="]:
                    group_idx = group_idx - 2
                group_idx = group_idx + 1
                
            tokens_list[it_tl] = Parser.delete_tokens(tokens_list[it_tl], [Token.TOKEN_DICT["="]])

        return tokens_list

    def __prepare_testbench__(self) -> list[Token]:

        file_content_copy_merged = Parser.prepare_file(self.file_content)
        tokens = Parser.define_tokens(file_content_copy_merged)
        tokens = Parser.change_tokens(tokens, [Token.TOKEN_DICT["*"]], [Token.TOKEN_DICT["\n"]])
        tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT["*"]])
        tokens = Parser.group_tokens(tokens, [Token.DEFAULT_ID])
        tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT[" "], Token.TOKEN_DICT["\t"], Token.TOKEN_DICT[","]])
        # tokens = Parser.delete_after_tokens(tokens, [Token.TOKEN_DICT["\n"]], [Token.TOKEN_DICT["\\"]])
        # tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT["\\"]])
        tokens = Parser.split_tokens(tokens, [Token.TOKEN_DICT["\n"]])

        return tokens

    def parse_testbench(self) -> list[SebaSpice]:
        tokens = self.__prepare_testbench__()
    
    def parse_corner_gen(self) -> SebaCorner:
        
        tokens = self.__prepare_corner_gen__()

        pm_wrong_arg_num_corner = lambda t, fc:\
            f"Wrong number of arguments; line: {t.line}, col: {t.column}\n"\
            f"{fc[t.line-1]}"\
            f"{"^"*(len(fc[t.line-1])-1)}"
        
        pm_missing_corner = lambda t, n, fc:\
            f"Missing corners: {n}; line: {t.line}\n"\
            f"{fc[t.line-1]}"\
            f"{"^"*(len(fc[t.line-1])-1)}"
        
        pm_wrong_def_corner = lambda t, fc:\
            f"Definition of corner after corner_gen is not allowed; line: {t.line}, col: {t.column}\n"\
            f"{fc[t.line-1]}"\
            f"{"^"*(len(fc[t.line-1])-1)}"
        
        pm_corner_duplicated = lambda t, fc:\
            f"Corner already defined earlier: {t.line}\n"\
            f"{fc[t.line-1]}"\
            f"{"^"*(len(fc[t.line-1])-1)}"

        pm_empty_array = lambda t, fc:\
            f"Empty array; line: {t.line}, col: {t.column}\n"\
            f"{fc[t.line-1]}"\
            f"{"^"*(len(fc[t.line-1])-1)}"
        
        pm_wrong_val_num_corner = lambda t1, t2, fc:\
            f"Discrapency in number of values or correlated arrays; line: {t1.line}, col: {t1.column}\n"\
            f"{fc[t1.line-1]}"\
            f"{"-"*(t1.column-1)}^{"-"*(t2.column-t1.column-1)}^"
        
        pm_unknown_corner_command = lambda t, fc:\
            f"Unknown corner command; line: {t.line} col: {t.column}\n"\
            f"{fc[t.line-1]}"\
            f"{"^"*(len(fc[t.line-1]))}"

        corners_def = []
        corners_gen = []
        corners_name = []

        corner_defenition_finish = False

        for it_tl, tl in enumerate(tokens):
            
            cmd = [x.value for x in tl]

            if cmd[0] == "lib" or cmd[0] == "param":
                if len(cmd) != 2:
                    raise WrongCornerDefinition(pm_wrong_arg_num_corner(tl[0], self.file_content))
                
                if corner_defenition_finish:
                    raise DefinitionAfterCornerGen(pm_wrong_def_corner(tl[0], self.file_content))
                
                if cmd[1] in corners_name:
                    CornerDuplication(pm_corner_duplicated(tl[0], self.file_content))

                corners_name.append(cmd[1])
                corners_def.append(Corner(cmd[0], cmd[1]))
                
            elif cmd[0] == "corner_gen":
                if len(cmd)-1 != len(corners_def):
                    raise MissingCornerValue(pm_wrong_arg_num_corner(tl[0], self.file_content))
                
                values = [t.value for t in tl[1:]]
                grouping = [t.group for t in tl[1:]]

                if len(values) != len(corners_def):
                    raise MissingCorner(pm_missing_corner(tl[0], len(corners_def)-len(values), self.file_content))

                len_val = -1
                last_group = -1

                for it_g in range(len(grouping)):
                    grp = grouping[it_g]
                    val = values[it_g]

                    if len(val) == 0:
                        raise EmptyCornerArray(pm_empty_array(tl[it_g+1], self.file_content))

                    if last_group != grp:
                        last_group = grp
                        len_val = len(val)
                        continue
                    
                    if len_val != len(val):
                        raise Exception(pm_wrong_val_num_corner(tl[it_g], tl[it_g+1], self.file_content))

                corners_gen.append(CornerGenerator(corners_def, values, grouping))

            else:
                raise UnknownCornerCommand(pm_unknown_corner_command(tl[0], self.file_content))

        if len(corners_gen) == 0:
            raise Exception("Corner generator line not found")

        seba_corner = SebaCorner(corners_gen)

        return seba_corner
    

    def parse_seba_config(self) -> SebaConfig:

        tokens = self.__prepare_seba_config__()
        
        pm_wrong_num_cmd = lambda tl, fc:\
            f"Wrong number of arguments; row: {tl.line}, col: {tl.column}\n"\
            f"{fc[tl.line-1]}"\
            f"{"^"*(len(fc[tl.line-1])-1)}"
        
        pm_unknown_cmd = lambda tl, fc:\
            f"Unknown command; row: {tl.line}, col: {tl.column}\n"\
            f"{fc[tl.line-1]}"\
            f"{"^"*(len(fc[tl.line-1])-1)}"


        seba_config = SebaConfig()

        for it_tl, tl in enumerate(tokens):

            if len(tl) == 1:
                raise WrongNumberConfigCommands(pm_wrong_num_cmd(tl[0], self.file_content))

            cmd = [x.value for x in tl]

            if cmd[0].upper() == "NAME":
                if len(tl) != 2:
                    raise WrongNumberConfigCommands(pm_wrong_num_cmd(tl[0], self.file_content))
                seba_config.name = cmd[1]

            elif cmd[0].upper() == "CONTROL":
                if len(tl) != 2:
                    raise WrongNumberConfigCommands(pm_wrong_num_cmd(tl[0], self.file_content))
                seba_config.control = cmd[1]

            elif cmd[0].upper() == "TESTBENCH":
                if len(tl) != 2:
                    raise WrongNumberConfigCommands(pm_wrong_num_cmd(tl[0], self.file_content))
                seba_config.testbench = cmd[1]

            elif cmd[0].upper() == "CORNERS":
                if len(tl) != 2:
                    raise WrongNumberConfigCommands(pm_wrong_num_cmd(tl[0], self.file_content))
                seba_config.corners = cmd[1]

            elif cmd[0].upper() == "SCRIPT":
                if len(tl) != 2:
                    raise WrongNumberConfigCommands(pm_wrong_num_cmd(tl[0], self.file_content))
                seba_config.script = cmd[1]

            elif cmd[0].upper() == "MEAS":
                if len(tl) != 2:
                    raise WrongNumberConfigCommands(pm_wrong_num_cmd(tl[0], self.file_content))
                seba_config.meas = cmd[1]

            elif cmd[0].upper() == "PLOT":
                if len(tl) != 2:
                    raise WrongNumberConfigCommands(pm_wrong_num_cmd(tl[0], self.file_content))
                seba_config.plot = cmd[1]

            elif cmd[0].upper() == "EXTRACTION":
                if len(tl) < 2:
                    raise WrongNumberConfigCommands(pm_wrong_num_cmd(tl[0], self.file_content))
                seba_config.extraction = cmd[1:]

            else:
                raise UnknownConfigCommand(pm_unknown_cmd(tl[0], self.file_content))

        if seba_config.name == None:
            raise MissingNameConfig(f"Cannot find \"NAME\" directive in configuration file.")

        if SebaArguments.isDebugOn or DEBUG:
            seba_config.print_config()


        return seba_config