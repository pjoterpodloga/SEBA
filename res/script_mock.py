from ngspice_utils import *

import pandas as pd
import glob

raw_files = glob.glob("*.raw_*")

vout_result = [0.]*len(raw_files)
idiv_result = [0.]*len(raw_files)

for rw in raw_files:

    corner_number = int(rw.split("_")[-1])

    parse_ngspice_raw(rw)

    vout = Signal.get_signal("v(vout)")
    idiv = Signal.get_signal("i(R3)")

    vout_at_0p5 = Signal.cross(vout, 0.5)
    idiv_at_0p5 = np.abs(Signal.cross(idiv, 0.5))

    print(f"vout @ 0.5V: {get_value_with_prefix(vout_at_0p5)}")
    print(f"idiv @ 0.5V: {get_value_with_prefix(idiv_at_0p5)}")

    vout_result[corner_number] = vout_at_0p5
    idiv_result[corner_number] = idiv_at_0p5

data = {"vout": vout_result, "idiv": idiv_result}
df = pd.DataFrame(data)
df.to_csv("measure.csv")
