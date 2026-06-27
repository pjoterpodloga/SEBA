
DEBUG = True

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

class SebaInputArguments:
    s_help = f"-h"
    l_help = f"--help"
    m_help = f"{s_help}, {l_help}\t\t\tShow this message"

    s_setup = f"-s"
    l_setup = f"--setup"
    m_setup = f"{s_setup}, {l_setup} <repo_path>\t\tSetup repository with provided <repo_path>"

    l_setup_force = f"--setup_force"
    m_setup_force = f"  , {l_setup_force} <repo_path>\tForcing setup of reposiotory with provided <repo_path>"\
                     "exisitng path will be removed"
    
    l_setup_debug = f"--setup_debug"
    m_setup_debug = f" , {l_setup_debug} <repo_path>\tSetup repository with provided <repo_path> for debug purposes"

    s_debug = f"-d"
    l_debug = f"--debug"
    m_debug = f"{s_debug}, {l_debug}\t\t\tShowing debug info"

    s_build = f"-b"
    l_build = f"--build"
    m_build = f"{s_build}, {l_build}\t\t\tBuild simulation directory from files provided in configuration file"

    l_build_force = f"--build_force"
    m_build_force = f"  , {l_build_force}\t\tForcing build simulation directory"

    s_sim = f"-s"
    l_sim = f"--simulate"
    m_sim = f"{s_sim}, {l_sim}\t\tPerfor simulations on builded simulation directory"

    l_debug_files = f"--debug_files"
    m_debug_files = f" , {l_debug_files}\t\tCreate debug files for testing purposes"