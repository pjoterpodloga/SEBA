from seba.utils import Corner, CornerGenerator
from seba.utils import TextFormat

test_corner_generator_pass_desc = "Valid corners generator"
def test_corner_generator_pass():

    corners_test = []
    values_test = []
    grouping_test = []
    result_test = []

    corners_test_1 = []
    corners_test_1.append(Corner("lib", "name1"))
    corners_test_1.append(Corner("param", "name2"))
    corners_test_1.append(Corner("param", "name3"))
    corners_test_1.append(Corner("lib", "name4"))
    corners_test.append(corners_test_1)

    values_test_1 = [["value1"],
                     ["value2"],
                     ["value3"],
                     ["value4"]]
    values_test.append(values_test_1)
    
    grouping_test_1 = [1, 2, 3, 4]
    grouping_test.append(grouping_test_1)

    result_test_1 = ["value1 value2 value3 value4"]
    result_test.append(result_test_1)


    corners_test_2 = []
    corners_test_2.append(Corner("lib", "name1"))
    corners_test_2.append(Corner("param", "name2"))
    corners_test_2.append(Corner("param", "name3"))
    corners_test_2.append(Corner("lib", "name4"))
    corners_test.append(corners_test_2)

    values_test_2 = [["value1.1", "value1.2"],
                     ["value2"],
                     ["value3"],
                     ["value4"]]
    values_test.append(values_test_2)
    
    grouping_test_2 = [1, 2, 3, 4]
    grouping_test.append(grouping_test_2)

    result_test_2 = ["value1.1 value2 value3 value4",
                     "value1.2 value2 value3 value4"]
    result_test.append(result_test_2)


    corners_test_3 = []
    corners_test_3.append(Corner("lib", "name1"))
    corners_test_3.append(Corner("param", "name2"))
    corners_test_3.append(Corner("param", "name3"))
    corners_test_3.append(Corner("lib", "name4"))
    corners_test.append(corners_test_3)

    values_test_3 = [["value1.1", "value1.2"],
                     ["value2"],
                     ["value3"],
                     ["value4"]]
    values_test.append(values_test_3)
    
    grouping_test_3 = [1, 2, 3, 4]
    grouping_test.append(grouping_test_3)

    result_test_3 = ["value1.1 value2 value3 value4",
                     "value1.2 value2 value3 value4"]
    result_test.append(result_test_3)

    corners_test_4 = []
    corners_test_4.append(Corner("lib", "name1"))
    corners_test_4.append(Corner("param", "name2"))
    corners_test_4.append(Corner("param", "name3"))
    corners_test_4.append(Corner("lib", "name4"))
    corners_test.append(corners_test_4)

    values_test_4 = [["value1.1", "value1.2"],
                     ["value2.1", "value2.2"],
                     ["value3"],
                     ["value4"]]
    values_test.append(values_test_4)
    
    grouping_test_4 = [1, 1, 2, 3]
    grouping_test.append(grouping_test_4)

    result_test_4 = ["value1.1 value2.1 value3 value4",
                     "value1.2 value2.2 value3 value4"]
    result_test.append(result_test_4)

    corners_test_5 = []
    corners_test_5.append(Corner("lib", "name1"))
    corners_test_5.append(Corner("param", "name2"))
    corners_test_5.append(Corner("param", "name3"))
    corners_test_5.append(Corner("lib", "name4"))
    corners_test.append(corners_test_5)

    values_test_5 = [["value1.1", "value1.2"],
                     ["value2.1", "value2.2"],
                     ["value3"],
                     ["value4"]]
    values_test.append(values_test_5)
    
    grouping_test_5 = [1, 2, 3, 4]
    grouping_test.append(grouping_test_5)

    result_test_5 = ["value1.1 value2.1 value3 value4",
                     "value1.1 value2.2 value3 value4",
                     "value1.2 value2.1 value3 value4",
                     "value1.2 value2.2 value3 value4"]
    result_test.append(result_test_5)

    corners_test_5 = []
    corners_test_5.append(Corner("lib", "name1"))
    corners_test_5.append(Corner("param", "name2"))
    corners_test_5.append(Corner("param", "name3"))
    corners_test_5.append(Corner("lib", "name4"))
    corners_test.append(corners_test_5)

    values_test_5 = [["value1.1", "value1.2"],
                     ["value2.1", "value2.2"],
                     ["value3.1", "value3.2"],
                     ["value4.1", "value4.2"]]
    values_test.append(values_test_5)
    
    grouping_test_5 = [1, 1, 1, 1]
    grouping_test.append(grouping_test_5)

    result_test_5 = ["value1.1 value2.1 value3.1 value4.1",
                     "value1.2 value2.2 value3.2 value4.2",]
    result_test.append(result_test_5)


    corners_test_6 = []
    corners_test_6.append(Corner("param", "xname1"))
    corners_test_6.append(Corner("param", "xname2"))
    corners_test.append(corners_test_6)

    values_test_6 = [["value1.1", "value1.2", "value1.3"],
                     ["value2.1", "value2.2", "value2.3"]]
    values_test.append(values_test_6)

    grouping_test_6 = [1, 2]
    grouping_test.append(grouping_test_6)

    result_test_6 = ["value1.1 value2.1",
                     "value1.1 value2.2",
                     "value1.1 value2.3",
                     "value1.2 value2.1",
                     "value1.2 value2.2",
                     "value1.2 value2.3",
                     "value1.3 value2.1",
                     "value1.3 value2.2",
                     "value1.3 value2.3"]
    result_test.append(result_test_6)
    

    for it_t in range(len(corners_test)):
        c = corners_test[it_t]
        v = values_test[it_t]
        g = grouping_test[it_t]
        r = result_test[it_t]

        try:
            corner_gen = CornerGenerator(c, v, g)
            ret = corner_gen.corner_list()
            assert ret == r, f"{ret}\n{r}"
        except Exception as ex:
            print(ex)
            return False

    return True

if __name__ == "__main__":
    
    if test_corner_generator_pass():
        print(f"{TextFormat.format("[PASSED]", fmt="Bg")} {test_corner_generator_pass_desc}")
    else:
        print(f"{TextFormat.format("[FAILED]", fmt="Br")} {test_corner_generator_pass_desc}")
    