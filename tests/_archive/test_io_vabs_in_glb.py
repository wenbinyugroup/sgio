import sys
from sgio.iofunc import readLoadCsv

# Wrap in main to prevent execution during test collection
if __name__ == '__main__':
    fn = sys.argv[1]
    smdim = int(sys.argv[2])
    model = int(sys.argv[3])

    rcases = readLoadCsv(fn, smdim, model)

    print(rcases)



# import sgio

# fn_sg = 'uh60a.sg'
# model = 'BM2'

# f1 = 4.677700e+04
# f2 = 2.507620e+02
# f3 = 4.149390e+02
# m1 = -3.061000e+02
# m2 = -1.613190e+03
# m3 = 2.727670e+03

# sff = '16.6e'

# # sg = sgio.read(
# #     fn=fn_sg, file_format='vabs', model=model
# # )
# # print(sg)


# load = [f1, f2, f3, m1, m2, m3]
# state = sgio.State(data=load)
# state_case = sgio.StateCase()
# state_case.addState(name='load', state=state)

# fn_glb = f'{fn_sg}.glb'
# sgio.write(
#     sg=None,
#     fn=fn_glb,
#     file_format='vabs',
#     analysis='d',
#     model=model,
#     macro_responses=[state_case,],
#     sff=sff
#     )
