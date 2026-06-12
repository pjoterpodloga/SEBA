DEBUG = True

class SebaInputArguments:
    s_help = f"-h"
    l_help = f"--help"
    m_help = f"{s_help}, {l_help}\t\t\tShow this message"

    s_setup = f"-s"
    l_setup = f"--setup"
    m_setup = f"{s_setup}, {l_setup} <repo_path>\t\tSetup repository with provided <repo_path>"

    l_setup_force = f"--setup_force"
    m_setup_force = f"  , {l_setup_force} <repo_path>\tForcing setup of reposiotory with provided <repo_path>\n\
                      \t\t\t\texisitng path will be removed"