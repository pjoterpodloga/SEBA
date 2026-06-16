from seba.arguments import SebaArguments
from seba.utils import UnknownArgumentError, MissingArgumentError
from seba.utils import TextFormat

def test_seba_argument_parse_pass() -> bool:
    mock_repo_name = "<repo_name>"
    mock_unknown_argument = "<unknown_argument>"

    mock_arguments_pass = [
    ["/"],
    ["/", "-h"],
    ["/", "--help"],    
    ["/", "-h", mock_unknown_argument],
    ["/", "--help", mock_unknown_argument],

    ["/", "-s", mock_repo_name],
    ["/", "--setup", mock_repo_name],
    ["/", "--setup_force", mock_repo_name],
    ["/", "-d"],

    ["/", "--debug"],
    ]

    mock_arguments_pass_checks = [
    [False, False, False, False, ""],

    [False, True, False, False, ""],
    [False, True, False, False, ""],
    [False, True, False, False, ""],
    [False, True, False, False, ""],

    [False, False, True, False, mock_repo_name],
    [False, False, True, False, mock_repo_name],
    [False, False, False, True, mock_repo_name],
    [True, False, False, False, ""],

    [True, False, False, False, ""],
    ]

    result = None
    try:
        for it_arg in range(len(mock_arguments_pass)):
            seba_arguments = SebaArguments(mock_arguments_pass[it_arg])
            seba_arguments.parse()

            assert seba_arguments.isDebugOn == mock_arguments_pass_checks[it_arg][0]
            assert seba_arguments.isShowHelpOn == mock_arguments_pass_checks[it_arg][1]
            assert seba_arguments.isSetupOn == mock_arguments_pass_checks[it_arg][2]
            assert seba_arguments.isSetupForceOn == mock_arguments_pass_checks[it_arg][3]
            assert seba_arguments.repoPath == mock_arguments_pass_checks[it_arg][4]

    except Exception as ex:
        return False

    return True

def test_seba_argument_parse_fail() -> bool:
    mock_repo_name = "<repo_name>"
    mock_unknown_argument = "<unknown_argument>"
    
    mock_arguments_fail = [
    ["/", "h"],
    ["/", "help"],
    ["/", mock_unknown_argument, "-h"],
    ["/", mock_unknown_argument, "--h"],
    ["/", "-s"],
    ["/", "--setup"],
    ["/", "s"],
    ["/", "setup"],
    ["/", "s", mock_repo_name],
    ["/", "setup", mock_repo_name],
    ["/", "d"],
    ["/", "-d", mock_repo_name],
    ["/", "debug"]
    ]

    for it_arg in range(len(mock_arguments_fail)):
        try:
            seba_arguments = SebaArguments(mock_arguments_fail[it_arg])
            seba_arguments.parse()
            
            return False
        except Exception as ex:
            assert UnknownArgumentError == type(ex) or MissingArgumentError == type(ex)

    return True
    

if __name__ == "__main__":
    if test_seba_argument_parse_pass():
        print(f"{TextFormat.format("[PASSED]", fmt="Bg")} Valid argument parsing")
    else:
        print(f"{TextFormat.format("[FAILED]", fmt="Br")} Valid argument parsing")

    if test_seba_argument_parse_fail():
        print(f"{TextFormat.format("[PASSED]", fmt="Bg")} Invalid argument parsing")
    else:
        print(f"{TextFormat.format("[FAILED]", fmt="Br")} Invalid argument parsing")
