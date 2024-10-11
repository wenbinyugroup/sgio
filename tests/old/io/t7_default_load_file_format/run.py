import sys
from msgd.model.io import readLoadCsv


fn = sys.argv[1]
smdim = int(sys.argv[2])
model = int(sys.argv[3])

rcases = readLoadCsv(fn, smdim, model)

print(rcases)
