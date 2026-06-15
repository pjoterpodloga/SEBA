from enum import Enum

from src.logger import *
from src.seba_config import *
from src.seba_corners import *
from src.seba_core import CornerGenerator, Corner, Token, TokenCorner

class SebaParser:

    def __init__(self, file_content):
        self.file_content = file_content

    def __prepare_file__(self, file_content: list[str]) -> str:
        file_content_copy = self.file_content.copy()
        file_content_copy.append("\n")

        file_content_copy_merged = "".join(file_content_copy)

        return file_content_copy_merged

    def __define_tokens_type__(self, file_content: str) -> list[Token]:
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

    def __change_token_type__(self, tokens: list[Token], target: list[int], until: list[int]) -> list[Token]:

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

    def __delete_token_type__(self, tokens: list[Token], target: list[int]) -> list[Token]:

        for it_t in range(len(tokens)-1, -1, -1):
            tt = tokens[it_t].type

            if tt in target:
                tokens.pop(it_t)

        return tokens
    
    def __group_token_type__(self, tokens: list[Token], target: list[int]) -> list[Token]:
        
        found_target = False
        current_target = -1

        grouped_value = ""

        grouped_token = Token()

        popped_token = Token()

        for it_t in range(len(tokens)-1, -1, -1):
            
            tt = tokens[it_t].type
            tv = tokens[it_t].value

            if tt != current_target and found_target:
                grouped_token = popped_token
                grouped_token.value = grouped_value
                tokens.insert(it_t+1, grouped_token)
                found_target = False

            if tt in target and not found_target:
                grouped_value = ""
                current_target = tt
                found_target = True

            if found_target:
                grouped_value = tv + grouped_value
                popped_token = tokens.pop(it_t)
        
        return tokens
    
    def __split_tokens__(self, tokens: list[Token], target: int) -> list[list[Token]]:
        
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

        if len(tmp_group) != 0:
            result.append(tmp_group)

        return result

    def __delete_after_token_type__(self, tokens: list[Token], target: list[int], until: list[int]) -> list[Token]:

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
    
    def __bound_by_token_type__(self, tokens: list[Token], target: list[int], until: list[int]) -> list[Token]:

        until_found = False

        pm_second_character_found = lambda t1, t2, fc:  f"Found second \"{t2.value}\" token; row: {t2.line}, col: {t2.column}\n"\
                                                        f"{fc[t2.line-1]}"\
                                                        f"{"~"*(t2.column-1)}^{"~"*((t1.column)-(t2.column)-1)}^"
        
        last_ut_token = None

        grouped_tokens = []
        popped_token = None
        for it_t in range(len(tokens)-1, -1, -1):

            tt = tokens[it_t].type

            if tt in target and until_found:
                last_ut_token = tokens[it_t]
                until_found = False
                tokens.insert(it_t, Token(popped_token.type, grouped_tokens, popped_token.line, popped_token.column))
                grouped_tokens = []
                continue

            if tt in target and not until_found:
                raise Exception(pm_second_character_found(last_ut_token, tokens[it_t], self.file_content))
                

            if tt in until and not until_found:
                until_found = True
                last_ut_token = tokens[it_t]
                continue

            if tt in until and until_found:
                raise Exception(pm_second_character_found(last_ut_token, tokens[it_t], self.file_content))

            if until_found:
                popped_token = tokens.pop(it_t)
                grouped_tokens.append(popped_token.value)

        return tokens
    
    def __check_surrounding_token_type__(self, tokens: list[Token], target: list[int], legal_surrounding: list[int]):
        pass

        return tokens
            
        

    def __prepare_seba_config__(self, file_content: list[str]) -> list[list[Token]]:
        
        file_content_copy_merged = self.__prepare_file__(file_content)
        tokens = self.__define_tokens_type__(file_content_copy_merged)
        tokens = self.__change_token_type__(tokens, [Token.TOKEN_DICT["#"]], [Token.TOKEN_DICT["\n"]])
        tokens = self.__delete_token_type__(tokens, [Token.TOKEN_DICT["#"]])
        tokens = self.__group_token_type__(tokens, [Token.DEFAULT_ID])
        tokens = self.__delete_token_type__(tokens, [Token.TOKEN_DICT[" "], Token.TOKEN_DICT["\t"]])
        tokens = self.__delete_after_token_type__(tokens, [Token.TOKEN_DICT["\n"]], [Token.TOKEN_DICT["\\"]])
        tokens = self.__delete_token_type__(tokens, [Token.TOKEN_DICT["\\"]])
        tokens = self.__split_tokens__(tokens, [Token.TOKEN_DICT["\n"]])

        return tokens
    
    def __prepare_corner_gen__(self, file_content: list[str]) -> list[list[Token]]:
        
        file_content_copy_merged = self.__prepare_file__(file_content)
        tokens = self.__define_tokens_type__(file_content_copy_merged)
        tokens = self.__change_token_type__(tokens, [Token.TOKEN_DICT["#"]], [Token.TOKEN_DICT["\n"]])
        tokens = self.__delete_token_type__(tokens, [Token.TOKEN_DICT["#"]])
        tokens = self.__group_token_type__(tokens, [Token.DEFAULT_ID, Token.TOKEN_DICT["="]])
        tokens = self.__delete_token_type__(tokens, [Token.TOKEN_DICT[" "], Token.TOKEN_DICT["\t"], Token.TOKEN_DICT[","]])
        tokens = self.__delete_after_token_type__(tokens, [Token.TOKEN_DICT["\n"]], [Token.TOKEN_DICT["\\"]])
        tokens = self.__delete_token_type__(tokens, [Token.TOKEN_DICT["\\"]])
        tokens = self.__check_surrounding_token_type__(tokens, [Token.TOKEN_DICT["="]], [Token.TOKEN_DICT["["], Token.TOKEN_DICT["]"]])
        tokens = self.__delete_token_type__(tokens, [Token.TOKEN_DICT[","]])
        tokens = [TokenCorner.from_token(t) for t in tokens]
        tokens_list = self.__split_tokens__(tokens, [Token.TOKEN_DICT["\n"]])
        for it_tl in range(len(tokens_list)):
            tokens_list[it_tl] = self.__bound_by_token_type__(tokens_list[it_tl], [Token.TOKEN_DICT["["]], [Token.TOKEN_DICT["]"]])
            tokens_list[it_tl] = self.__delete_token_type__(tokens_list[it_tl], [Token.TOKEN_DICT["["], Token.TOKEN_DICT["]"]])
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
                
            tokens_list[it_tl] = self.__delete_token_type__(tokens_list[it_tl], [Token.TOKEN_DICT["="]])

        return tokens_list

    
    def parse_corner_gen(self) -> SebaCorner:
        
        tokens = self.__prepare_corner_gen__(self.parse_corner_gen)

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

        tokens = self.__prepare_seba_config__(self.file_content)
        
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