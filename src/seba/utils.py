from seba.constants import AnsiCode as ac

### TODO: Add all posible text formating
class TextFormat:
    @classmethod
    def bold(cls, string):
        return ac.bold_on+string+ac.bold_off
    @classmethod
    def underline(cls, string):
        return ac.underline_on+string+ac.underline_off
    @classmethod
    def slow_blink(cls, string):
        return ac.slow_blink_on+string+ac.blink_off
    @classmethod
    def rapid_blink(cls, string):
        return ac.rapid_blink_on+string+ac.blink_off
    @classmethod
    def italic(cls, string):
        return ac.italic_on+string+ac.italic_off
    @classmethod
    def crossed_out(cls, string):
        return ac.crossed_out_on+string+ac.crossed_out_off
    @classmethod
    def black(cls, string):
        return ac.text_black+string+ac.text_default
    @classmethod
    def red(cls, string):
        return ac.text_red+string+ac.text_default
    @classmethod
    def green(cls, string):
        return ac.text_green+string+ac.text_default
    @classmethod
    def blue(cls, string):
        return ac.text_blue+string+ac.text_default
    @classmethod
    def yellow(cls, string):
        return ac.text_yellow+string+ac.text_default
    @classmethod
    def magenta(cls, string):
        return ac.text_magenta+string+ac.text_default
    @classmethod
    def cyan(cls, string):
        return ac.text_cyan+string+ac.text_default
    @classmethod
    def white(cls, string):
        return ac.text_white+string+ac.text_default
    @classmethod
    def format(cls, string, fmt):
        
        for it, f in enumerate(fmt):
            if f == "B":
                string = cls.bold(string)
                continue
            if f == "I":
                string = cls.italic(string)
                continue
            if f == "U":
                string = cls.underline(string)
                continue
            if f == "C":
                string = cls.crossed_out(string)
                continue
            if f == "r":
                string = cls.red(string)
                continue
            if f == "g":
                string = cls.green(string)
                continue
            if f == "b":
                string = cls.blue(string)
                continue
            if f == "y":
                string = cls.yellow(string)
                continue
            if f == "w":
                string = cls.white(string)
                continue
            if f == "m":
                string = cls.magenta(string)
                continue
            if f == "c":
                string = cls.cyan(string)
        return string

### TODO: Add ID generation to folders and default files for fast search and easy caching
### TODO: Refactor those classes

class DirectoryEntity:
    __last__id__ = 0

    def __init__(self):
        self.__id__ = DirectoryEntity.__last__id__
        DirectoryEntity.__last__id__ = DirectoryEntity.__last__id__ + 1

    def __assign_new_id__(self):
        self.__id__ = DirectoryEntity.__last__id__
        DirectoryEntity.__last__id__ = DirectoryEntity.__last__id__ + 1

class DefaultFile(DirectoryEntity):
    def __init__(self, name, content=""):
        super().__init__()
        self.name = name
        self.content = content

class TemporaryFile(DefaultFile):
    def __init__(self, name, content="", pattern=None):
        super().__init__(name, content)
        self.pattern = pattern

        if pattern == None:
            raise Exception("Pattern for temporary file cannot be empty.")

class Folder(DirectoryEntity):
    def __init__(self, name, branches):
        super().__init__()
        self.name = name
        self.branches = branches

    def resolve_tree_list(self, depth=1, eot=False):
        joint = "├"
        horiz = "─"
        vert = "│"
        knee = "└"

        result = [f"{self.name}"]
        next_eot = False

        for it_br, br in enumerate(self.branches):
            
            if (it_br == len(self.branches)-1):
                next_eot = True

            if (type(br) == Folder or type(br) == TemporaryFolder):
                lines = br.resolve_tree_list(depth=depth+1, eot=next_eot)
                for it_l, l in enumerate(lines):
                    if it_l == 0 and not next_eot:
                        result.append(f"{joint}{horiz} {l}")
                    elif it_l == 0 and next_eot:
                        result.append(f"{knee}{horiz} {l}")
                    elif it_l != 0 and not next_eot:
                        result.append(f"{vert}  {l}")
                    elif it_l != 0 and next_eot:
                        result.append(f"   {l}")
            elif (type(br) == DefaultFile or type(br) == TemporaryFile):
                if (it_br == len(self.branches)-1):
                    result.append(f"{knee}{horiz} {br.name}")
                else:
                    result.append(f"{joint}{horiz} {br.name}")
            else:
                if (it_br == len(self.branches)-1):
                    result.append(f"{knee}{horiz} {br}")
                else:
                    result.append(f"{joint}{horiz} {br}")

        return result
    
    def resolve_tree_string(self):
        result = self.resolve_tree_list()

        tmp = ""
        for r in result:
            tmp = tmp + "\t" + r + "\n"
        result = tmp

        return result

    def resolve_tree(self):
        result = []

        found_subdir = False

        for br in self.branches:

            if (type(br) == Folder or type(br) == TemporaryFolder):
                found_subdir = True
                ret = br.resolve_tree()

                for r in ret:
                    result.append(self.name + "/" + r)

        if found_subdir == False:
            result.append(self.name)

        return result
    
    def resolve_default_files(self, depth=1, return_placeholders = False):
        result = []

        found_default_file = False
        found_subdir = False

        for br in self.branches:
            if (type(br) == Folder or type(br) == TemporaryFolder):
                found_subdir = True
                ret = br.resolve_default_files(depth=depth+1, return_placeholders = return_placeholders)

                for r in ret:
                    result.append([self.name + "/" + r[0], r[1]])
            
            elif (type(br) == DefaultFile or type(br) == TemporaryFile):
                found_default_file = True
                result.append([self.name + "/" + br.name, br.content])

        if (not found_default_file or not found_subdir) and depth != 1 and return_placeholders:
            result.append([self.name + "/" + "__placeholder__", ""])

        return result

    def resolve_tree_directory(self, folder_tree):
        result = []
        
        for br in self.branches:
            
            if (type(br) == Folder or type(br) == TemporaryFolder):
                if (br.name == folder_tree.name):
                    result.append(self.name + "/" + folder_tree.name)

                ret = br.resolve_tree_directory(folder_tree)

                for r in ret:
                    result.append(self.name + "/" + r)

        return result
    
    def resolve_temporary_tree_directory(self):
        result = []
        
        for br in self.branches:
            
            if (type(br) == TemporaryFolder):
                result.append(self.name + "/" + br.name)

            if (type(br) == Folder or type(br) == TemporaryFolder):
                ret = br.resolve_temporary_tree_directory()

                for r in ret:
                    result.append(self.name + "/" + r)

        return result
    
    def resolve_temporary_file_pattern(self):
        result = []
        
        for br in self.branches:
            
            if (type(br) == TemporaryFile):
                result.append(self.name + "/" + br.pattern)

            if (type(br) == Folder or type(br) == TemporaryFolder):
                ret = br.resolve_temporary_file_pattern()

                for r in ret:
                    result.append(self.name + "/" + r)


        return result

    def insert_branch(self, branch: DirectoryEntity):
        branch.__assign_new_id__()
        self.branches.append(branch)

    def replace_branches(self, branches: list[DirectoryEntity]):
        for it_b in range(len(branches)):     
            branches[it_b].__assign_new_id__()
        self.branches = branches

    def generate_gitignore(self, header="# .gitignore file"):
        result = ""
        
        tmp_file_pattern = self.resolve_temporary_file_pattern()
        tmp_folder_name = self.resolve_temporary_tree_directory()

        result = header + "\n"
        
        for tfn in tmp_folder_name:
            result = result + tfn + "/\n"

        result = result + "\n"
        
        for tfp in tmp_file_pattern:
            result = result + tfp + "\n"

        return result

class TemporaryFolder(Folder):
    def __init__(self, name, branches, pattern=None):
        super().__init__(name, branches)
        self.pattern = pattern

class Corner:
    def __init__(self, corner_type, corner_name, corner_value=None):
        self.type = corner_type
        self.name = corner_name
        self.value= corner_value

class CornerGenerator:
    def __init__(self, corners: list[Corner], values: list[list[str]], grouping: list[int]):
        self.corners = corners
        self.values = values
        self.grouping = grouping

        if  len(corners) != len(values) or\
            len(corners) != len(grouping) or\
            len(values) != len(grouping):

            raise Exception("Number of corners, value or/and grouping are not the same.")

        for c in corners:
            pass

        total_number_of_corners = 1
        current_group = -1

        for it, v in enumerate(self.values):
            if current_group == self.grouping[it]:
                continue
            total_number_of_corners = total_number_of_corners * len(v)
            current_group = self.grouping[it]

        self.tnoc = total_number_of_corners

        self.__resolved_corners__ = self.resolve()

    def resolve(self) -> list[Corner]:
        index_list = [-1]*len(self.corners)

        it_gen = 0
        current_group = -1

        resolved_corners = []

        while it_gen < self.tnoc:
            it_mod = 0
            it_grp = 0
            current_group = -1
            for it_c in range(len(self.corners)-1, -1, -1):
                grp = self.grouping[it_c]
                if current_group != grp:
                    current_group = grp
                    it_mod = (it_gen >> it_grp) % len(self.values[it_c])
                    if len(self.values[it_c]) != 1:
                        it_grp = it_grp + 1

                index_list[it_c] = it_mod

            corner = []
            for it_il, il in enumerate(index_list):
                t = self.corners[it_il].type
                n = self.corners[it_il].name
                v = self.values[it_il][il]
                corner.append(Corner(t, n, v))

            resolved_corners.append(corner)

            it_gen = it_gen + 1

        return resolved_corners
        
    def corner_list_header(self) -> list[str]:
        result = []

        for it_c, c in enumerate(self.corners):
            t = c.type
            n = c.name
            result.append(f"{t} {n}")
            
        return result

    def corner_line(self, n_corner: int) -> str:
        result = []

        for it_c, c in enumerate(self.__resolved_corners__[n_corner]):
            v = c.value

            if it_c == 0:
                result = f"{v}"
            else:
                result = f"{result} {v}"

        return result

    def spice_block(self, n_corner: int) -> list[str]:
        result = []

        for it_c, c in enumerate(self.__resolved_corners__[n_corner]):
            t = c.type
            n = c.name
            v = c.value

            if t == "lib":
                result.append(f".{t} {n} {v}")
            elif t == "param":
                result.append(f".{t} {n}={v}")

        return result
        
    def spice_list(self) -> list[str]:
        result = []

        for it_tnoc in range(self.tnoc):
            result.append(self.spice_block(it_tnoc))

        return result
        
    def corner_list(self) -> list[str]:
        result = []

        for it_tnoc in range(self.tnoc):
            result.append(self.corner_line(it_tnoc))

        return result

class WrongNumberConfigCommands(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class UnknownConfigCommand(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class MissingNameConfig(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class WrongCornerDefinition(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class MissingCorner(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class DefinitionAfterCornerGen(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class CornerDuplication(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class EmptyCornerArray(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class MissingCornerValue(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class UnknownCornerCommand(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class Token:
    DEFAULT_ID = 1

    SEARCH_VALUES = [" ", "\t", "\\", "#", "=", "[", "]", ",", "\n", ":"]

    TOKEN_DICT = {x: i + 2 for i, x in enumerate(SEARCH_VALUES)}

    def __init__(self, file_id=None, type=None, value=None, line=None, column=None):
        self.file_id = file_id
        self.type = type
        self.value = value
        self.line = line
        self.column = column

class TokenCorner(Token):
    def __init__(self,file_id=None, type=None, value=None, line=None, column=None):
        super().__init__(file_id, type, value, line, column)
        self.group = -1

    @classmethod
    def from_token(cls, token: Token):
        return cls(file_id=token.file_id, type=token.type, value=token.value, line=token.line, column=token.column)

class Parser:

    __last_file_id__ = 0
    __file_content__ = []

    @classmethod
    def prepare_file(cls, file_content: list[str]) -> str:
        file_content_copy = file_content.copy()
        file_content_copy.append("\n")

        file_content_copy_merged = "".join(file_content_copy)

        return file_content_copy_merged

    @classmethod
    def define_tokens(cls, file_content: str) -> list[Token]:
        token_dict = Token.TOKEN_DICT

        cls.__file_content__.append(file_content)

        token = [Token(file_id=cls.__last_file_id__, type=0,)]*len(file_content)
        token_id = cls.__last_file_id__
        cls.__last_file_id__ = cls.__last_file_id__ + 1
        token_keys = token_dict.keys()

        row = 1
        col = 1

        for it_fc, fc in enumerate(file_content):
            if fc in token_keys:
                token[it_fc] = Token(file_id=token_id, type=token_dict[fc], value=fc, line=row, column=col)
            else:
                token[it_fc] = Token(file_id=token_id, type=Token.DEFAULT_ID, value=fc, line=row, column=col)

            col = col + 1

            if fc == "\n":
                row = row + 1
                col = 1

        return token

    @classmethod
    def change_tokens(cls, tokens: list[Token], target: list[int], until: list[int]) -> list[Token]:

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
    def delete_tokens(cls, tokens: list[Token], target: list[int]) -> list[Token]:

        for it_t in range(len(tokens)-1, -1, -1):
            tt = tokens[it_t].type

            if tt in target:
                tokens.pop(it_t)

        return tokens
    
    @classmethod
    def group_tokens(cls, tokens: list[Token], target: list[int]) -> list[Token]:
        
        found_target = False
        current_target = -1

        grouped_value = ""

        grouped_token = None

        popped_token = None

        for it_t in range(len(tokens)-1, -2, -1):
            
            if it_t == -1:
                if found_target:
                    grouped_token = popped_token
                    grouped_token.value = grouped_value
                    tokens.insert(it_t+1, grouped_token)
                break

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
  
    @classmethod  
    def split_tokens(cls, tokens: list[Token], target: int) -> list[list[Token]]:
        
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

    @classmethod
    def delete_after_tokens(cls, tokens: list[Token], target: list[int], until: list[int]) -> list[Token]:

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
    def bound_by_token(cls, tokens: list[Token], target: list[int], until: list[int]) -> list[Token]:

        until_found = False

        pm_second_character_found = lambda t1, t2, fc:\
            f"Found second \"{t2.value}\" token; row: {t2.line}, col: {t2.column}\n"\
            f"{fc[t1.line-1]}"\
            f"{"~"*(t1.column-1)}^{"~"*((t2.column)-(t1.column)-1)}^"

        last_ut_token = None

        grouped_tokens = []
        popped_token = None
        for it_t in range(len(tokens)-1, -1, -1):

            tt  = tokens[it_t].type
            tid = tokens[it_t].file_id

            if tt in target and until_found:
                last_ut_token = tokens[it_t]
                until_found = False
                tokens.insert(it_t+1, type(popped_token)(file_id=popped_token.file_id, type=popped_token.type, value=grouped_tokens, line=popped_token.line, column=popped_token.column))
                grouped_tokens = []
                continue

            if tt in target and not until_found:
                raise SecondCharacterError(pm_second_character_found(tokens[it_t], last_ut_token, cls.__file_content__[tid]))
                

            if tt in until and not until_found:
                until_found = True
                last_ut_token = tokens[it_t]
                continue

            if tt in until and until_found:
                raise SecondCharacterError(pm_second_character_found(last_ut_token, tokens[it_t], cls.__file_content__[tid]))

            if until_found:
                popped_token = tokens.pop(it_t)
                grouped_tokens.insert(0, popped_token.value)

        return tokens
    
    @classmethod
    def check_surrounding_token(cls, tokens: list[Token], target: list[int], legal_surrounding: list[int]):
        ### TODO: Write body of check surrounding of tokens function

        return tokens
    

class UnknownArgumentError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class MissingArgumentError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class SecondCharacterError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

        