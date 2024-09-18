import sys
import sgio

i = 1
fn_in = sys.argv[i]
i += 1
file_format_in = sys.argv[i]
i += 1
format_version = sys.argv[i]

if file_format_in.lower().startswith('s'):
    i += 1
    smdim = int(sys.argv[i])
else:
    smdim = 1

i += 1
fn_out = sys.argv[i]
i += 1
file_format_out = sys.argv[i]


sg = sgio.read(fn_in, file_format_in, format_version, smdim)
sgio.write(sg, fn_out, file_format_out, mesh_only=True)
