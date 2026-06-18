from seba.utils import TextFormat
from test_seba_arguments import *
from test_seba_corner import *
from test_seba_parser import *

class Testcase:
    def __init__(self, test, desc):
        self.test = test
        self.desc = desc

testcases = [
    Testcase(test=test_seba_argument_parse_pass, desc=test_seba_argument_parse_pass_desc),
    Testcase(test=test_seba_argument_parse_fail, desc=test_seba_argument_parse_fail_desc),
    Testcase(test=test_corner_generator_pass, desc=test_corner_generator_pass_desc),
    Testcase(test=test_seba_parser_corner_pass, desc=test_seba_parser_corner_pass_desc)
]

if __name__ == "__main__":

    it_max = len(testcases)
    for it_tc, tc in enumerate(testcases):
        _it_tc = it_tc + 1
        if tc.test():
            print(f"[{_it_tc}/{it_max}] {TextFormat.format("[PASSED]", fmt="Bg")} {tc.desc}")
        else:
            print(f"[{_it_tc}/{it_max}] {TextFormat.format("[FAILED]", fmt="Br")} {tc.desc}")