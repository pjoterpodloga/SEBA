from seba.utils import TextFormat
from test_seba_arguments import *
from test_seba_corner import *

class Testcase:
    def __init__(self, test, desc):
        self.test = test
        self.desc = desc

all_tests = [
    [test_seba_argument_parse_pass],
    [test_seba_argument_parse_fail],
    test_corner_generator_pass,
    test_corner_generator_fail
]

testcases = [
    Testcase(test=test_seba_argument_parse_pass, desc=test_seba_argument_parse_pass_desc),
    Testcase(test=test_seba_argument_parse_fail, desc=test_seba_argument_parse_fail_desc),
    Testcase(test=test_corner_generator_pass, desc=test_corner_generator_pass_desc),
    Testcase(test=test_corner_generator_fail, desc=test_corner_generator_fail_desc),
]

if __name__ == "__main__":

    it_max = len(testcases)
    for it_tc, tc in enumerate(testcases):
        _it_tc = it_tc + 1
        if tc.test():
            print(f"[{_it_tc}/{it_max}] {TextFormat.format("[PASSED]", fmt="Bg")}")
        else:
            print(f"[{_it_tc}/{it_max}] {TextFormat.format("[PASSED]", fmt="Br")} {tc.desc}")