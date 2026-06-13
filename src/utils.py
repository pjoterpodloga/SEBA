from src.constants import AnsiCode

### TODO: Add all posible text formating
class TextFormat:
    @classmethod
    def bold(cls, string):
        return AnsiCode.bold_on+string+AnsiCode.bold_off
    @classmethod
    def red(cls, string):
        return AnsiCode.text_red+string+AnsiCode.text_default
    @classmethod
    def green(cls, string):
        return AnsiCode.text_green+string+AnsiCode.text_default
    @classmethod
    def blue(cls, string):
        return AnsiCode.text_blue+string+AnsiCode.text_default
    @classmethod
    def yellow(cls, string):
        return AnsiCode.text_yellow+string+AnsiCode.text_default
    @classmethod
    def format(cls, string, fmt):
        
        for it, f in enumerate(fmt):
            if f == "B":
                string = cls.bold(string)
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
        return string

class DefaultFile:
    def __init__(self, name, content=""):
        self.name = name
        self.content = content

class TemporaryFile(DefaultFile):
    def __init__(self, name, content="", pattern=None):
        super().__init__(name, content)
        self.pattern = pattern

        if pattern == None:
            raise Exception("Pattern for temporary file cannot be empty.")

class Folder:
    def __init__(self, name, branches):
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

    def insert_branch(self, branch):
        self.branches.append(branch)

    def replace_branches(self, branches):
        self.branches = branches

    def generate_gitignore(self):
        result = ""
        
        tmp_file_pattern = self.resolve_temporary_file_pattern()
        tmp_folder_name = self.resolve_temporary_tree_directory()

        for it_tfp in range(len(tmp_file_pattern)):
            tmp_file_pattern[it_tfp] = tmp_file_pattern[it_tfp].replace("<repo_name>/", "")
        
        for it_tfn in range(len(tmp_folder_name)):
            tmp_folder_name[it_tfn] = tmp_folder_name[it_tfn].replace("<repo_name>/", "")

        result = "# Default SEBA .gitignore file\n"
        
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