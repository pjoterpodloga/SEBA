import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class Signal:
    __x_axis = []
    __x_axis_name = ""
    __y_data = []
    __variables_name = []
    __last_index = 0
    __name_mapping = dict()
    __sweep_current_key = -1
    __sweep_mapping = dict()
    __sweep_axis = []

    def __init__(self, name=None, data=None):
        if (name == None):
            raise Exception("Name parameter cant be \"None\".")

        if (data == None):
            self.name = name
            self.y_data = type(self).__name_mapping[name]

        if (type(self).__sweep_current_key is not -1):
            name = f"{name}#{type(self).__sweep_current_key}"

        if (type(data) == list):
            data = np.array(data)

        if (len(data) != len(type(self).__x_axis)):
            raise Exception("Length of vectors are not the same.")

        type(self).__y_data.append(data)
        type(self).__variables_name.append(name)
        type(self).__name_mapping[name] = type(self).__last_index
        type(self).__last_index = type(self).__last_index + 1

        self.name = name
        self.y_data = data

    @classmethod
    def get_x_axis(cls):
        return cls.__x_axis
    
    @classmethod
    def get_sweep_axis(cls):
        return cls.__sweep_axis

    @classmethod
    def get_sweep_value(cls, index):
        return cls.__sweep_axis[index]

    @classmethod
    def get_signal(cls, name, sweep_key=None):
        if (cls.__sweep_current_key is -1):
            return cls.__y_data[cls.__name_mapping[name]]
        if ((name.find("#") != -1 and name.split("#")[1].isdigit())):
            return cls.__y_data[cls.__name_mapping[name]]
        
        sweep = [
            cls.__y_data[cls.__name_mapping[k]]
            for k in sorted(cls.__name_mapping, key=lambda x: int(x.split("#")[1]))
            if k.startswith(name+"#")
        ]

        return np.stack(sweep)
        
    
    @classmethod
    def value_at(cls, sig, at=None):
        if at is None:
            return sig[0]
        return np.interp(at, cls.__x_axis, sig)
    
    @classmethod
    def cross(cls, sig1, sig2, at_range=None, first_occurence=True, return_idx=False, return_y=False):
        x = cls.__x_axis
        
        if (at_range is not None):
            if (len(at_range) != 2):
                raise("at_range should have only 2 values.")
            if (at_range[0] > at_range[1]):
                Warning("at_range[1] should be bigger than ar_range[0]. Values has been swaped")
                tmp = at_range[0]
                at_range[0] = at_range[1]
                at_range[1] = tmp
            if (at_range[0] < 0):
                Warning("at_range[0] cant be less than 0. Setting at_range[0] to 0")
                at_range[0] = 0
            
            _, idx_start = cls.cross(cls.__x_axis, at_range[0], return_idx=True)
            _, idx_stop = cls.cross(cls.__x_axis, at_range[1], return_idx=True)

            if (len(idx_stop) == 0):
                Warning("at_range[1] exceeded max range of x axis")
                idx_stop = len(cls.get_x_axis()) - 1

            idx_start = idx_start[0]
            idx_stop = idx_stop[0]

            if (type(sig1) is np.ndarray):
                sig1 = sig1[idx_start:idx_stop]
            if (type(sig2) is np.ndarray):
                sig2 = sig2[idx_start:idx_stop]

            x = x[idx_start:idx_stop]

        d = sig1 - sig2
        idx = np.where(np.diff(np.sign(d)))[0]

        if (first_occurence):
            idx = idx[0:1]

        x_cross = []

        for i in idx:
            x0, x1 = x[i], x[i+1]
            d0, d1 = d[i], d[i+1]

            _x_cross = x0 - d0 * (x1 - x0) / (d1 - d0)

            x_cross.append(_x_cross)

        x_cross = np.array(x_cross)

        y_cross = np.interp(x_cross, x, sig1)

        if return_idx and return_y:
            return x_cross, y_cross, idx
        elif return_y:
            return x_cross, y_cross
        elif return_idx:
            return x_cross, idx
        else:
            return x_cross
    
    @classmethod
    def derivative(cls, sig):
        return np.gradient(sig, cls.__x_axis)

    @classmethod
    def xmax(cls, sig):
        ym = cls.ymax(sig)
        return cls.cross(sig, ym)
    
    @classmethod
    def xmin(cls, sig):
        ym = cls.ymin(sig)
        return cls.cross(sig, ym)
    
    @classmethod
    def ymax(cls, sig):
        return np.max(sig)
    
    @classmethod
    def ymin(cls, sig):
        return np.min(sig)

    @classmethod
    def magnitude(cls, sig):
        return np.abs(sig)
    
    @classmethod
    def magnitude_db(cls, sig):
        return 20*np.log10(cls.magnitude(sig))

    @classmethod
    def phase_rad(cls, sig):
        return np.angle(sig)

    @classmethod
    def phase_deg(cls, sig):
        return cls.phase_rad(sig) / np.pi * 180.0

    @classmethod
    def phase_rad_unwrapped(cls, sig):
        ph_rad = cls.phase_rad(sig)
        ph_idx_pos = np.where(np.diff(ph_rad) >=  np.pi*0.975)[0] + 1
        ph_idx_neg = np.where(np.diff(ph_rad) <= -np.pi*0.975)[0] + 1
        
        ph_idx = np.concatenate((ph_idx_pos, ph_idx_neg))
        ph_idx.sort()

        sign = 0

        for i, idx in enumerate(ph_idx):
            if (idx in ph_idx_pos):
                sign = -1
            else:
                sign = 1

            if (i == len(ph_idx) - 1):
                ph_rad[idx:] = ph_rad[idx:] + (sign * 2 * np.pi)
            else:
                ph_rad[idx:ph_idx[i+1]] = ph_rad[idx:ph_idx[i+1]] + (sign * 2 * np.pi)

        return ph_rad
    
    @classmethod
    def phase_deg_unwrapped(cls, sig):
        return cls.phase_rad_unwrapped(sig) / np.pi * 180.0

    @classmethod
    def phase_margin(cls, sig):
        f0 = cls.cross(cls.magnitude_db(sig), 0)
        ph = cls.value_at(cls.phase_rad_unwrapped(sig), f0)
        return np.pi - np.abs(ph)

    @classmethod
    def phase_margin_deg(cls, sig):
        return cls.phase_margin(sig) / np.pi * 180.

    @classmethod
    def plot(cls, sig):
        set_log_scale = 0
        if (cls.__x_axis_name == "frequency"):
            set_log_scale = 1

        if (type(sig) == list):
            fig, axs = plt.subplots(len(sig), 1)
            for i, a in enumerate(axs):
                if (set_log_scale):
                    a.semilogx(cls.__x_axis, sig[i])
                else:
                    a.plot(cls.__x_axis, sig[i])
                a.grid()
        else:
            fig, ax = plt.subplots()
            if (set_log_scale):
                ax.semilogx(cls.__x_axis, sig)
            else:
                ax.plot(cls.__x_axis, sig)
            ax.grid()

    @classmethod
    def set_x_axis(cls, data, name):        
        if (type(data) == list):
            data = np.array(data)
        cls.__x_axis = data
        cls.__x_axis_name = name

    @classmethod
    def set_sweep_axis(cls, data, name):
        if (type(data) == list):
            data = np.array(data)
        cls.__sweep_axis = data
        cls.__sweep_axis_name = name

    @classmethod 
    def set_sweep_key(cls, n_sweep):
        cls.__sweep_current_key = n_sweep

    @classmethod
    def reset(cls):
        cls.__x_axis = []
        cls.__x_axis_name = ""
        cls.__y_data = []
        cls.__variables_name = []
        cls.__last_index = 0
        cls.__name_mapping = dict()
        cls.__sweep_mapping = dict()
        cls.__sweep_axis = []
        


def parse_ngspice_raw(filepath):
    Signal.reset()
    return __parse_ngspice_raw_ascii(filepath)

def __parse_ngspice_raw_ascii(filepath):

    variables = []
    line_num_variables_map = dict()
    variables_line_num_map = dict()
    data = []

    # Reading whole file to memory
    with open(filepath, 'r') as f:
        lines = f.readlines()

    var_line_index = 0
    val_line_index = 0

    n_of_points = 0

    idx_start_of_sweep = []
    sweep_axis_values = []
    sweep_axis_name = ""

    flags = []

    # Finding headers line numbers
    for i, line in enumerate(lines):
        line = line.strip()

        if (line.startswith("Sweep:")):
            sweep_axis_name = line.strip().split(":")[1]

        if (line.startswith("Sweep value:")):
            idx_start_of_sweep.append(i)
            line = line.strip().split(":")[1]
            sweep_axis_values.append(float(line))

        if (line.startswith("No. Points:") and n_of_points == 0):
            n_of_points = int(line.strip().split(":")[1])

        if (line.startswith("Flags:") and not flags):
            found_flags = line[6:].strip().split(",")
            flags.extend(found_flags)

        if (line.startswith("Variables:") and var_line_index == 0):
            var_line_index = i
            continue

        if (line.startswith("Values:") and val_line_index == 0):
            val_line_index = i
            continue

    if (idx_start_of_sweep):
        Signal.set_sweep_axis(sweep_axis_values, sweep_axis_name)

    is_value_real = False
    is_value_complex = False

    if (flags.count("real") > 0):
        is_value_real = True
    if (flags.count("complex") > 0):
        is_value_complex = True

    num_of_variables = val_line_index - var_line_index - 1

    print(f"Number of points per sweep: {n_of_points}")
    print(f"Number of sweeps: {len(idx_start_of_sweep)}")
    print(f"Variables start at line number: {var_line_index}")
    print(f"Values start at line number: {val_line_index}")
    print(f"Number of variables: {num_of_variables}")

    # Finding variables names
    for i in range(var_line_index + 1, val_line_index):
        line = lines[i].strip().split('\t')

        local_line_number = int(line[0])
        variable_name = line[1]

        variables.append(variable_name)

        line_num_variables_map[local_line_number] = variable_name
        variables_line_num_map[variable_name] = local_line_number

    print(f"Found {len(variables)} variables.")
    print(f"Variables:")

    for v in variables:
        print(f"\t{v}")

    args_parse = []
    args_parse.append(num_of_variables)
    args_parse.append(val_line_index)
    args_parse.append(n_of_points)
    args_parse.append(is_value_real)
    args_parse.append(is_value_complex)
    args_parse.append(variables)
    args_parse.append(variables_line_num_map)

    header_size = val_line_index
    value_size = n_of_points*(num_of_variables+1)

    if (sweep_axis_values):
        for i, v in enumerate(sweep_axis_values):
            start_idx = i*(header_size + value_size) + 2
            stop_idx = (i+1)*(header_size + value_size) + 1
            data.extend(__parse_sweep_data(lines[start_idx:stop_idx], i, args_parse))
    else:
        data.extend(__parse_sweep_data(lines, -1, args_parse))

    return data, variables

def __parse_sweep_data(lines, n_sweep, args):

    num_of_variables = args[0]
    val_line_index = args[1]
    n_of_points = args[2]
    is_value_real = args[3]
    is_value_complex = args[4]
    variables = args[5]
    variables_line_num_map = args[6]

    if (n_sweep is not -1):
        val_line_index = val_line_index - 2

    local_index = 0
    counted_points = 0

    values = [[] for _ in range(num_of_variables)]

    for i, line in enumerate(lines[val_line_index + 1:]):
        line = line.split()

        if (counted_points > n_of_points - 1):
            pass
            break

        if (len(line) == 2 and line[0].isdigit()):
            value_idx = 1
        elif (len(line) == 1):
            value_idx = 0
        else:
            counted_points = counted_points + 1
            local_index = 0
            continue

        if (is_value_real):
            value = float(line[value_idx])

        if (is_value_complex):
            line = line[value_idx].split(",")

            if (value_idx == 0):
                value = float(line[0])+(float(line[1])*1j)
            if (value_idx == 1):
                value = float(line[0])

        values[local_index].append(value)

        local_index = local_index + 1
    
    data = dict()

    Signal.set_sweep_key(n_sweep)

    for i, v in enumerate(variables):
        data[v] = values[variables_line_num_map[v]]
        if (i == 0):
            Signal.set_x_axis(data=values[0], name=variables[0])
            continue
        Signal(name=v, data=values[variables_line_num_map[v]])

    return data

def cross(x, y1, y2, return_idx=False, return_y=False):
    d = y1 - y2
    idx = np.where(np.diff(np.sign(d)))[0]

    x_cross = []

    for i in idx:
        x0, x1 = x[i], x[i+1]
        d0, d1 = d[i], d[i+1]

        _x_cross = x0 - d0 * (x1 - x0) / (d1 - d0)

        x_cross.append(_x_cross)

    x_cross = np.array(x_cross)

    y_cross = np.interp(x_cross, x, y1)

    if return_idx and return_y:
        return x_cross, y_cross, idx
    elif return_y:
        return x_cross, y_cross
    elif return_idx:
        return x_cross, idx
    else:
        return x_cross

def derivative(x, y):
    return np.gradient(y, x)

def value_at(x, y, at=None):
    if at is None:
        return y[0]
    return np.interp(at, x, y)

prefix_to_mag = dict()
prefix_to_mag['T'] = 12
prefix_to_mag['G'] = 9
prefix_to_mag['M'] = 6
prefix_to_mag['k'] = 3
prefix_to_mag[' '] = 0
prefix_to_mag['m'] = -3
prefix_to_mag['u'] = -6
prefix_to_mag['n'] = -9
prefix_to_mag['p'] = -12

mag_to_prefix = dict()
mag_to_prefix[12]  = 'T'
mag_to_prefix[9]   = 'G'
mag_to_prefix[6]   = 'M'
mag_to_prefix[3]   = 'k'
mag_to_prefix[0]   = ''
mag_to_prefix[-3]  = 'm'
mag_to_prefix[-6]  = 'u'
mag_to_prefix[-9]  = 'n'
mag_to_prefix[-12] = 'f'

def get_value_with_prefix(value):
    if (type(value) == np.ndarray):
        try:
            value = value[0]
        except:
            value = None

    try:
        mag = np.log10(np.abs(value))/3.0
        mag = np.floor(mag) * 3
        base = np.round(value/10.0**mag, decimals=4)
        result = f"{base}{mag_to_prefix[mag]}"
    except:
        result = " ||Something went wrong!|| "

    
    return result

def print_prefix(value, force=None):
    
    if (type(value) == np.ndarray):
        value = value[0]

    if (force is None):
        result = get_value_with_prefix(value)

    print(result)
