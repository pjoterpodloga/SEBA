from seba.utils import TextFormat
from seba.parser import SebaParser

test_seba_parser_corner_pass_desc = "Valid corner gen file parser"
def test_seba_parser_corner_pass():
    corner_file_content_list = []
    corner_file_parse_result = []
    
    corner_file_content_1 = [
        "lib lib1\n",
        "lib lib2\n",
        "param param1\n",
        "param param2\n",
        "corner_gen [value1] [value2] [value3] [value4]\n"
    ]
    corner_file_content_list.append(corner_file_content_1)

    corner_file_parse_result_1 = [[
       [".lib lib1 value1",
        ".lib lib2 value2",
        ".param param1=value3",
        ".param param2=value4",],
        "lib lib1",
        "lib lib2",
        "param param1",
        "param param2",
        "value1 value2 value3 value4"
    ]]
    corner_file_parse_result.append(corner_file_parse_result_1)

    corner_file_content_2 = [
        "lib lib1\n",
        "lib lib2\n",
        "param param1\n",
        "param param2\n",
        "corner_gen [value1.1, value1.2] [value2] [value3] [value4]\n"
    ]
    corner_file_content_list.append(corner_file_content_2)

    corner_file_parse_result_2 = [[
       [".lib lib1 value1.1",
        ".lib lib2 value2",
        ".param param1=value3",
        ".param param2=value4",],
        [".lib lib1 value1.2",
        ".lib lib2 value2",
        ".param param1=value3",
        ".param param2=value4",],
        "lib lib1",
        "lib lib2",
        "param param1",
        "param param2",
        "value1.1 value2 value3 value4",
        "value1.2 value2 value3 value4"
    ]]
    corner_file_parse_result.append(corner_file_parse_result_2)

    for it_cfcl, cfcl in enumerate(corner_file_content_list):
        parser = SebaParser(cfcl)
        corner_gen = parser.parse_corner_gen()

        spice_corners = corner_gen.generate_spice_corners()
        corner_list = corner_gen.generate_corner_list()

        result = spice_corners + corner_list

        for it_rr in range(len(corner_file_parse_result[it_cfcl])):
            for it_r in range(len(corner_file_parse_result[it_cfcl][it_rr])):
                try:
                    res = result[it_r]
                    ret = corner_file_parse_result[it_cfcl][it_rr][it_r]
                    assert res == ret, f"{res}\n{ret}"
                except Exception as ex:
                    print(ex)
                    return False

    return True


if __name__ == "__main__":
    if test_seba_parser_corner_pass():
        print(f"{TextFormat.format("[PASSED]", fmt="Bg")} {test_seba_parser_corner_pass_desc}")
    else:
        print(f"{TextFormat.format("[FAILED]", fmt="Br")} {test_seba_parser_corner_pass_desc}")
