class SebaCornerGeneration:

    class Corner:
        def __init__(self, corner_type, corner_name, corner_value=None):
            self.type = corner_type
            self.name = corner_name
            self.value= corner_value

    class CornerGenerator:
        def __init__(self, corners, values, grouping):
            self.corners = corners
            self.values = values
            self.grouping = grouping
            
            total_number_of_corners = 1
            current_group = -1

            for it, v in enumerate(self.values):
                if current_group == self.grouping[it]:
                    continue
                total_number_of_corners = total_number_of_corners * len(v)
                current_group = self.grouping[it]

            self.tnoc = total_number_of_corners

            self.resolved_corners = self.resolve()

        def resolve(self):
            index_list = [-1]*len(self.corners)

            it_gen = 0
            current_group = -1

            resolved_corners = []

            while it_gen < self.tnoc:
                it_mod = 0
                it_grp = 0
                current_group = -1
                for it_c in range(len(self.corners)-1, -1, -1):
                    grp = self.grouping[it_c]
                    if current_group != grp:
                        current_group = grp
                        it_mod = (it_gen >> it_grp) % len(self.values[it_c])
                        if len(self.values[it_c]) != 1:
                            it_grp = it_grp + 1

                    index_list[it_c] = it_mod

                corner = []
                for it_il, il in enumerate(index_list):
                    t = self.corners[it_il].type
                    n = self.corners[it_il].name
                    v = self.values[it_il][il]
                    corner.append(SebaCornerGeneration.Corner(t, n, v))

                resolved_corners.append(corner)

                it_gen = it_gen + 1

            return resolved_corners
        
        def corner_list_header(self):
            result = []

            for it_c, c in enumerate(self.corners):
                t = c.type
                n = c.name
                result.append(f"{t} {n}")
            
            return result

        def corner_line(self, n_corner):
            result = []

            for it_c, c in enumerate(self.resolved_corners[n_corner]):
                v = c.value

                if it_c == 0:
                    result = f"{v}"
                else:
                    result = f"{result} {v}"

            return result

        def spice_block(self, n_corner):
            result = []

            for it_c, c in enumerate(self.resolved_corners[n_corner]):
                t = c.type
                n = c.name
                v = c.value

                if t == "lib":
                    result.append(f".{t} {n} {v}")
                elif t == "param":
                    result.append(f".{t} {n}={v}")

            return result
        
        def spice_list(self):
            result = []

            for it_tnoc in range(self.tnoc):
                result.append(self.spice_block(it_tnoc))

            return result
        
        def corner_list(self):
            result = []

            for it_tnoc in range(self.tnoc):
                result.append(self.corner_line(it_tnoc))

            return result

    __corner_gen_file__ = None
    __corner_generators__ = None

    @classmethod
    def set_corner_gen_file(cls, corner_gen_file):
        cls.__corner_gen_file__ = corner_gen_file
        cls.__create_corners_generators__()

    @classmethod
    def __get_corners_generators__(cls):
        if cls.__corner_generators__ == None:
            raise Exception("Error occured while creating generators or corner generator file was not provided.")
        return cls.__corner_generators__

    @classmethod
    def __create_corners_generators__(cls):
        
        corner_gen_file_copy = cls.__corner_gen_file__.copy()

        error_encountered = False
        
        for it_cgc in range(len(corner_gen_file_copy)):
            corner_gen_file_copy[it_cgc] = f"{it_cgc+1}$"+corner_gen_file_copy[it_cgc].split("#")[0]+"#"

        parsed_corner = []

        for it_cgc, cg in enumerate(corner_gen_file_copy):
            
            substring_start = -1
            substring_stop = -1

            substrings = []

            for it_ch, ch in enumerate(cg):

                is_delimiter = (ch == " ") or (ch == "\t") or (ch == "#") or (ch == "$")
                is_substring_start = not is_delimiter and substring_start == -1
                is_substring_stop = is_delimiter and substring_start != -1 and substring_stop == -1

                if is_substring_start:
                    substring_start = it_ch
                
                if is_substring_stop:
                    substring_stop = it_ch

                substring_found = substring_start != -1 and substring_stop != -1

                if substring_found:
                    substrings.append(cg[substring_start : substring_stop])
                    substring_start = -1
                    substring_stop = -1

            parsed_corner.append(substrings)
        
        found_lib_param = True
        
        corners = []

        for it_pc, pc in enumerate(parsed_corner):
            c_type = None
            c_name = None

            if len(pc) <= 1:
                continue

            if pc[1] == "lib" or pc[1] == "param":
                c_type = pc[1]
                found_lib_param = True
            elif found_lib_param:
                break
            else:
                raise Exception(f"Wrong placement or missing corner type in line {pc[0]}")
                break
            
            if c_type != None and len(pc) != 3:
                raise Exception(f"Wrong number of parameters after corner type in line {pc[0]}")
                break

            c_name = pc[2]

            corners.append(SebaCornerGeneration.Corner(c_type, c_name))

        found_corner_gen = False

        corner_generators = []
        it_pc = 0

        for it_pc, pc in enumerate(parsed_corner):
            
            pc_copy = pc.copy()

            for it_pc_split in range(len(pc_copy)-1, -1, -1):
                split = pc_copy[it_pc_split].split("==")
                if len(split) != 1:
                    pc_copy.insert(it_pc_split, split)

            if len(pc_copy) <= 1:
                continue

            if pc_copy[1] == "corner_gen":
                found_corner_gen = True
            elif found_corner_gen:
                break
            else:
                continue

            if len(pc_copy) - 2 != len(corners):
                raise Exception(f"Wrong number of corners in corner_gen in line {pc[0]}")
                error_encountered = True
                break

            values = []
            grouping = []
            it_g = 0

            for v in pc[2:]:
                corr_v = v.split("==")

                ref_l = len(corr_v[0].split(","))

                for cv in corr_v:
                    cv = cv.replace("[", "")
                    cv = cv.replace("]", "")
                    if len(cv.split(",")) != ref_l:
                        raise Exception(f"Wrong number of paired corners in line {pc[0]}")
                        break
                    grouping.append(it_g)
                    values.append(cv.split(","))

                it_g = it_g + 1

            corner_generators.append(SebaCornerGeneration.CornerGenerator(corners, values, grouping))

        cls.__corner_generators__ = corner_generators
    
    @classmethod
    def generate_spice_corners(cls):
        result = []

        corners_generators = cls.__get_corners_generators__()

        for it_cg, cg in enumerate(corners_generators):
            result = result + cg.spice_list()
        
        return result
    
    @classmethod
    def generate_corner_list(cls):
        result = []

        corners_generators = cls.__get_corners_generators__()

        result = result + corners_generators[0].corner_list_header()

        for it_cg, cg in enumerate(corners_generators):
            result = result + cg.corner_list()
        
        return result