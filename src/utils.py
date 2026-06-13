class AnsiCode:
    reset               = "\033[0m" # Reset all text attributes to default
    bold_on             = "\033[1m" # Bold on
    faint_off           = "\033[2m" # Faint off
    italic_on           = "\033[3m" # Italic on
    underline_on        = "\033[4m" # Underline on
    slow_blink_on       = "\033[5m" # Slow blink on
    rapid_blink_on      = "\033[6m" # Rapid blink on
    reverse_video       = "\033[7m" # Reverse video on
    conceal_on          = "\033[8m" # Conceal on
    crossed_out_on      = "\033[9m" # Crossed-out on
    bold_off            = "\033[22m" # Bold off
    italic_off          = "\033[23m" # Italic off
    underline_off       = "\033[24m" # Underline off
    blink_off           = "\033[25m" # Blink off
    reverse_video_off   = "\033[27m" # Reverse video off
    conceal_off         = "\033[28m" # Conceal off
    crossed_out_off     = "\033[29m" # Crossed-out off

    # Text color
    text_black      = "\033[30m" # Set text color to black
    text_red        = "\033[31m" # Set text color to red
    text_green      = "\033[32m" # Set text color to green
    text_yellow     = "\033[33m" # Set text color to yellow
    text_blue       = "\033[34m" # Set text color to blue
    text_magenta    = "\033[35m" # Set text color to magenta
    text_cyan       = "\033[36m" # Set text color to cyan
    text_white      = "\033[37m" # Set text color to white
    text_default    = "\033[39m" # Reset text color to default

    # Background color
    bg_black        = "\033[40m" # Set background color to black
    bg_red          = "\033[41m" # Set background color to red
    bg_green        = "\033[42m" # Set background color to green
    bg_yellow       = "\033[43m" # Set background color to yellow
    bg_blue         = "\033[44m" # Set background color to blue
    bg_magenta      = "\033[45m" # Set background color to magenta
    bg_cyan         = "\033[46m" # Set background color to cyan
    bg_white        = "\033[47m" # Set background color to white
    bg_default      = "\033[49m" # Reset background color to default


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

class FolderTree:
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

            if (type(br) == FolderTree):
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
            elif (type(br) == DefaultFile):
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

            if (type(br) == FolderTree):
                found_subdir = True
                ret = br.resolve_tree()

                for r in ret:
                    result.append(self.name + "/" + r)

        if found_subdir == False:
            result.append(self.name)

        return result
    
    def resolve_default_files(self, depth=1):
        result = []

        found_default_file = False
        found_subdir = False

        for br in self.branches:
            if (type(br) == FolderTree):
                found_subdir = True
                ret = br.resolve_default_files(depth=depth+1)

                for r in ret:
                    result.append([self.name + "/" + r[0], r[1]])
            
            elif (type(br) == DefaultFile):
                found_default_file = True
                result.append([self.name + "/" + br.name, br.content])

        if (not found_default_file or not found_subdir) and depth != 1:
            result.append([self.name + "/" + "__placeholder__", ""])

        return result
    
    def resolve_tree_directory(self, folder_tree):
        result = []
        
        for br in self.branches:
            
            if (type(br) == FolderTree):
                if (br.name == folder_tree.name):
                    result.append(self.name + "/" + folder_tree.name)

                ret = br.resolve_tree_directory(folder_tree)

                for r in ret:
                    result.append(self.name + "/" + r)

        return result

    def insert_branch(self, branch):
        self.branches.append(branch)

    def replace_branches(self, branches):
        self.branches = branches

