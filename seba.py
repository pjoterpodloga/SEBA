#!/usr/bin/python3

from src.seba_utils import *

if __name__ == "__main__":

    print(root_tree.resolve_tree_string())

    if(len(sys.argv) == 1):
        SebaArguments.show_help(force=True)
        print("Script Terminated")
        exit(1)

    SebaArguments.parse()
    SebaArguments.show_help()

    SebaArguments.print_config()

    SebaSetupTool.setup_repository("tmp", True)
