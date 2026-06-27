from enum import Enum

from seba.constants import *
from seba.logger import *
from seba.arguments import *
from seba.config import *
from seba.corners import *
from seba.spice import *
from seba.utils import CornerGenerator, Corner, Token, TokenCorner, Parser
from seba.utils import WrongNumberConfigCommands, UnknownConfigCommand, MissingNameConfig
from seba.utils import MissingCorner, DefinitionAfterCornerGen, WrongCornerDefinition
from seba.utils import EmptyCornerArray, MissingCornerValue, UnknownCornerCommand
from seba.utils import CornerDuplication

class SebaParser:

    def __init__(self, config: SebaConfig, file_content: list[str]):

        self.config = config

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

    def __prepare_testbench__(self) -> list[list[Token]]:

        file_content_copy_merged = Parser.prepare_file(self.file_content)
        tokens = Parser.define_tokens(file_content_copy_merged)
        tokens = Parser.change_tokens(tokens, [Token.TOKEN_DICT["*"]], [Token.TOKEN_DICT["\n"]])
        tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT["*"]])
        tokens = Parser.alter_tokens(tokens, [Token.TOKEN_DICT["."]], Token.DEFAULT_ID)
        tokens = Parser.group_tokens(tokens, [Token.DEFAULT_ID])
        tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT[" "], Token.TOKEN_DICT["\t"], Token.TOKEN_DICT[","]])
        # tokens = Parser.delete_after_tokens(tokens, [Token.TOKEN_DICT["\n"]], [Token.TOKEN_DICT["\\"]])
        # tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT["\\"]])
        tokens = Parser.split_tokens(tokens, [Token.TOKEN_DICT["\n"]])

        return tokens

    def __prepare_control__(self) -> list[list[Token]]:
        file_content_copy_merged = Parser.prepare_file(self.file_content)
        tokens = Parser.define_tokens(file_content_copy_merged)
        tokens = Parser.change_tokens(tokens, [Token.TOKEN_DICT["*"]], [Token.TOKEN_DICT["\n"]])
        tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT["*"]])
        tokens = Parser.alter_tokens(tokens, [Token.TOKEN_DICT["."]], Token.DEFAULT_ID)
        tokens = Parser.group_tokens(tokens, [Token.DEFAULT_ID])
        tokens = Parser.delete_tokens(tokens, [Token.TOKEN_DICT[" "], Token.TOKEN_DICT["\t"], Token.TOKEN_DICT[","]])
        tokens = Parser.split_tokens(tokens, [Token.TOKEN_DICT["\n"]])
        return tokens

    def parse_control(self) -> SebaControl:

        AsyncLogger.info(f"Parsing control file: {self.config.control}")

        tokens = self.__prepare_control__()

        se_list = []

        ### TODO: extend parser for other control options

        for it_t, tl in enumerate(tokens):
            se = None

            if tl[0].value.upper() == "WRITE":
                se = ControlWriteDefinition(tl[1].value, [x.value for x in tl[2:]])
                se_list.append(se)
                continue
            
            if tl[0].value.upper() == "SET":
                if tl[2].value != "=":
                    raise Exception("Wrong definition of SET directive in .control block")
                se = ControlSetDefinition(tl[1].value, tl[3].value)
                se_list.append(se)
                continue

            se = GenericDefinition([x.value for x in tl])
            se_list.append(se)

        seba_control = SebaControl(se_list)

        return seba_control

    def parse_testbench(self) -> SebaTestbench:

        AsyncLogger.info(f"Parsing testbench file: {self.config.testbench}")

        tokens = self.__prepare_testbench__()

        se_list = []

        ### TODO: write proper exceptions for error handling

        for it_tl, tl in enumerate(tokens):
            se = None

            if tl[0].value == ".lib":
                if len(tl) != 3:
                    raise Exception("Incomplete library definition")

                se = LibraryDefinition(tl[1].value, tl[2].value)
                se_list.append(se)
                continue
            
            ### TODO: Add expresion handling, should be resolved at token parsing
            if tl[0].value.upper() == ".PARAM":
                if len(tl) != 4 or tl[2].value != "=":
                    raise Exception("Incomplete parameter definition")
                se = ParameterDefinition(tl[1].value, tl[3].value)
                se_list.append(se)
                continue

            if tl[0].value.upper() == ".TEMP":
                if len(tl) != 2:
                    raise Exception("Incomplete temperatur definition")
                se = TemperatureDefinition(tl[1].value)
                se_list.append(se)
                continue

            if tl[0].value.upper().startswith("X"):
                parameters = []
                first_parameter = -1
                for it_t, t in enumerate(tl):
                    if t.type == Token.TOKEN_DICT["="]:
                        if it_t == 0 or it_t == len(tl) - 1:
                            raise Exception("Incomplete device parameters definition")
                        if first_parameter == -1:
                            first_parameter = it_t - 1
                        parameters.append([tl[it_t-1].value, tl[it_t+1].value])

                if first_parameter == -1:
                    first_parameter = len(tl)

                nets = []
                for it_t, t in enumerate(tl[1:first_parameter]):
                    nets.append(t.value)

                se = DeviceDefinition(tl[0].value, nets, parameters)
                se_list.append(se)
                continue

            if tl[0].value.upper().startswith("R") or \
               tl[0].value.upper().startswith("L") or \
               tl[0].value.upper().startswith("C") or \
               tl[0].value.upper().startswith("V"):
                
                nets = []
                for it_t, t in enumerate(tl[1:len(tl)]):
                    nets.append(t.value)

                se = DeviceDefinition(tl[0].value, nets, [])
                se_list.append(se)
                continue
            
            ### TODO: add more probes handling
            if tl[0].value.upper() == ".PROBE":
                if len(tl) != 2:
                    raise Exception("Incomplete .probe directive")
                se = ProbeDefinition(tl[1].value)
                se_list.append(se)
                continue

            ### TODO: add more save options handling
            if tl[0].value.upper() == ".SAVE":
                if len(tl) != 2:
                    raise Exception("Incomplete .save directive")
                se = SaveDefinition(tl[1].value)
                se_list.append(se)
                continue

            ### TODO: add sweep type definition handling
            if tl[0].value.upper() == ".DC":
                se = DcAnalysisDefinition(tl[1].value, tl[2].value, tl[3].value, tl[4].value)
                se_list.append(se)

            if tl[0].value.upper() == ".SUBCKT":
                nets = []
                for it_t, t in enumerate(tl[2:]):
                    nets.append(t.value)
                se = SubcircuitDefinition(tl[1].value, nets)
                se_list.append(se)
                continue

            if tl[0].value.upper() == ".GLOBAL":
                if len(tl) != 2:
                    raise Exception("Incomplete .global directive definition")
                se = GlobalNetDefinition(tl[1])
                se_list.append(se)
                continue
            
            ### TODO: add .options directive handling
            if tl[0].value.upper() == ".OPTIONS":
                pass

            if tl[0].value.upper() == ".ENDS":
                if len(tl) != 1:
                    raise Exception("Wrong definition of .endc directive")
                se_list.append(EndSubcircuitDefinition())
                continue

            if tl[0].value.upper() == ".END":
                if len(tl) != 1:
                    raise Exception("Wrong definition of .end directive")
                se_list.append(EndDefinition())
                continue

        seba_spice = SebaTestbench(se_list)

        return seba_spice
            

    
    def parse_corner_gen(self) -> SebaCorner:

        AsyncLogger.info(f"Parsing corner gen file: {self.config.corners}")
        
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

        AsyncLogger.info(f"Parsing SEBA configuration file: {SebaArguments.sebaFile}")

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
        config_dir = SebaArguments.sebaFile.split("/")
        config_dir.pop()
        seba_config.config_dir = SebaArguments.executePath + "/" + "/".join(config_dir)

        for it_tl, tl in enumerate(tokens):

            if len(tl) == 1:
                raise WrongNumberConfigCommands(pm_wrong_num_cmd(tl[0], self.file_content))

            cmd = [x.value for x in tl]

            if cmd[0].upper() == "NAME":
                if len(tl) != 2:
                    raise WrongNumberConfigCommands(pm_wrong_num_cmd(tl[0], self.file_content))
                seba_config.name = cmd[1]
                seba_config.sim_dir = seba_config.config_dir + "/../tmp/simulations/" + seba_config.name

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