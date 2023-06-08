# import numpy as np
# from scipy import interpolate
import pprint
# import msgpi.utils.params as mup
import msgpi.utils.function as muf
import msgd.ext.rcas as mmr


# Pre-processing


def materialId2Name(data, sname, logger, *args, **kwargs):
    # pprt = pprint.PrettyPrinter(indent=4)
    # pprt.pprint(data)
    mdb = {
        1: 'AS4 12k/E7K8_0.0054',
        2: 'S2/SP381_0.0092',
        3: 'T650-35 12k/976_0.0052',
        4: 'T700 24K/E765_0.0056',
    }
    data[sname]['lam_spar_1'] = mdb[data[sname]['lamid_spar_1']]
    data[sname]['lam_front'] = mdb[data[sname]['lamid_front']]
    data[sname]['lam_back'] = mdb[data[sname]['lamid_back']]
    
    return


# def preProcessGeo(data, sname, logger, *args, **kwargs):
#     # Calculate embedded points
#     data[sname]['pfle1_a2'] = data[sname]['pnsmc_a2'] - data[sname]['nsmr'] - 0.005
#     data[sname]['pfle2_a2'] = data[sname]['wl_a2'] + 0.005
#     data[sname]['pfte1_a2'] = data[sname]['wt_a2'] - 0.01

#     return









# Post-processing

def dakota_postpro(data, sname, logger, *args, **kwargs):
    """ Post-process results from previous analysis steps.

    This is the last step in a Dakota evaluation.
    The goal is to calculate response/objective/constraint function values
    and store them in data['dakota']:

        data['dakota'] = {
            'descriptor1': value1,
            'descriptor2': value2,
            ...
        }
    """

    pprt = pprint.PrettyPrinter(indent=4)

    # cs_names = list(outputs['cs'].keys())
    blade_name = data['structures']['blade'][0]
    cs_names = data['structures']['cs']

    # weights = kwargs['weights']
    bp_names = kwargs['beam_properties']

    # Convert data into interpolation functions
    ref_bp_funcs = getRefPropFunctions()
    # ref_bp = kwargs['ref_properties']
    # ref_bp_func_type = ref_bp['function']
    # ref_bp_funcs = {}
    # if ref_bp_func_type == 'interpolation':
    #     intp_kind = ref_bp['kind']
    #     try:
    #         ref_bp_form = ref_bp['data_form']
    #     except KeyError:
    #         ref_bp_form = 'compact'
    #     if ref_bp_form == 'file':
    #         ref_bp_fn = ref_bp['file_name']
    #         ref_bp_format = ref_bp['data_format']
    #         if ref_bp_format == 'rcas_prop':
    #             ref_prop = mmr.readRcasProp(ref_bp_fn)
    #             ref_prop_request = ref_bp['data_request']
    #             for bpn, bpr in zip(bp_names, ref_prop_request):
    #                 # print('bpn: {}, bpr: {}'.format(bpn, bpr))
    #                 # print(ref_prop[bpr.upper()])
    #                 ref_bp_funcs[bpn] = muf.InterpolationFunction(
    #                     ref_prop[bpr.upper()]['x'],
    #                     ref_prop[bpr.upper()]['y'],
    #                     kind=intp_kind
    #                 )
            # ndimx = 1
            # ref_bp_funcs = mup.loadDataCSV(ref_bp_fn, ndimx, kind=intp_kind)
    # xscale = kwargs['xscale']

    # diffs = np.zeros(len(cs_names))
    diffs = {'gj': [], 'ei22': [], 'ei33': []}
    # mpls = np.zeros(len(cs_names))

    # Radial locations of cross-sections
    # rs = np.zeros(len(cs_names))
    rs = data[blade_name]['stations']
    for i, cs_name in enumerate(cs_names):
        cs_data = data[cs_name]

        # diff = []

        for bp_name in bp_names:
            # fn = pp[0]  # function name
            # rn = pp[1]  # response name
            # cs_args = pp[2]
            rn = bp_name + '_diff'

            # Get calculated value
            bp_cal = cs_data[bp_name]
            # if bp_name == 'mc2':
            #     bp_cal = bp_cal - cs_data['sc2']
            #     bp_name = bp_name + '_sc'

            # Get reference/target value
            bp_ref_name = bp_name + '_ref'
            ref_bp_func = ref_bp_funcs[bp_name]
            # print(rs[i]*xscale)
            bp_ref = float(ref_bp_func(rs[i]))
            # print(type(bp_ref).__name__)
            cs_data[bp_ref_name] = bp_ref

            r = (bp_cal - bp_ref) / bp_cal
            # diff.append(r)
            diffs[bp_name].append(r**2)

            cs_data[rn] = r
            data['dakota']['diff_{}_{}'.format(cs_name, bp_name)] = r


        # weighted_squared_diffs = [diff[i]**2 * weights[i] for i in range(len(diff))]
        # diffs[i] = sum(weighted_squared_diffs)

        # mpls[i] = cs_outputs['mu']

    # diff_obj = sum(diffs)
    # outputs['final'].insert(0, ['diff', diff_obj])
    data['dakota']['diff_gj'] = sum(diffs['gj'])
    data['dakota']['diff_eiyy'] = sum(diffs['ei22'])
    data['dakota']['diff_eizz'] = sum(diffs['ei33'])

    # ttm = 0
    # for i in range(int(len(rs) / 2)):
    #     ttm += (mpls[2*i] + mpls[2*i+1]) / 2.0 * (rs[2*i+1] - rs[2*i])
    # ttm = ttm * inputs['rotor_radius']
    # outputs['final'].insert(1, ['total_mass_c', ttm])


    # Process strength ratio
    sr_min = None

    for i, cs_name in enumerate(cs_names):
        for k, v in data[cs_name].items():
            if k.startswith('sr_case'):
                if not sr_min:
                    sr_min = v
                elif v > 0 and v < sr_min:
                    sr_min = v

    data['dakota']['sr_min'] = sr_min

    return





def getRefPropFunctions():
    ref_bp_funcs = {}

    # Radial station
    rprop =    [
        0.00000,       0.04658,       0.04659,       0.04713,       0.04714,
        0.07236,       0.08106,       0.09317,       0.09318,       0.10093,
        0.10094,       0.11397,       0.11398,       0.12999,       0.13000,
        0.15528,       0.15529,       0.18136,       0.18137,       0.19300,
        0.23292,       0.23293,       0.24874,       0.24875,       0.25901,
        0.28509,       0.28510,       0.33727,       0.33728,       0.38944,
        0.41553,       0.44161,       0.44162,       0.45090,       0.45091,
        0.46770,       0.49379,       0.49380,       0.49689,       0.51829,
        0.51830,       0.52095,       0.54811,       0.54812,       0.57526,
        0.60242,       0.60243,       0.62958,       0.65674,       0.65675,
        0.68390,       0.71106,       0.71107,       0.73575,       0.73576,
        0.76043,       0.76044,       0.78784,       0.78785,       0.80981,
        0.80982,       0.82298,       0.83450,       0.85404,       0.85522,
        0.85523,       0.85919,       0.85920,       0.86290,       0.86292,
        0.86293,       0.87933,       0.89947,       0.89948,       0.90373,
        0.91961,       0.92857,       0.93975,       0.93976,       0.95062,
        0.96366,       0.96367,       0.97562,       0.98758,       0.98759,
        1.00000,
            ];
    # Bending stiffness
    eiflap =   [
        0.38208E+06,     0.38208E+06,     0.38208E+06,     0.38208E+06,     0.38208E+06,
        0.38208E+06,     0.38208E+06,     0.38208E+06,     0.61405E+06,     0.61405E+06,
        0.61405E+06,     0.61405E+06,     0.61405E+06,     0.61405E+06,     0.19162E+06,
        0.19162E+06,     0.19162E+06,     0.19162E+06,     0.19162E+06,     0.19162E+06,
        0.19162E+06,     0.15417E+06,     0.15417E+06,     0.15417E+06,     0.15417E+06,
        0.15417E+06,     0.15417E+06,     0.15417E+06,     0.15417E+06,     0.15417E+06,
        0.15417E+06,     0.15417E+06,     0.15561E+06,     0.15561E+06,     0.15561E+06,
        0.15561E+06,     0.15561E+06,     0.16042E+06,     0.16042E+06,     0.16042E+06,
        0.16042E+06,     0.16042E+06,     0.16042E+06,     0.16042E+06,     0.16042E+06,
        0.16042E+06,     0.16088E+06,     0.16088E+06,     0.16088E+06,     0.16319E+06,
        0.16319E+06,     0.16319E+06,     0.16319E+06,     0.14239E+06,     0.14237E+06,
        0.12709E+06,     0.12709E+06,     0.12709E+06,     0.12709E+06,     0.12709E+06,
        0.12282E+06,     0.12282E+06,     0.12451E+06,     0.12744E+06,     0.12744E+06,
        0.12744E+06,     0.12744E+06,     0.12531E+06,     0.12531E+06,     0.12531E+06,
        0.12922E+06,     0.25792E+06,     0.43040E+06,     0.38256E+06,     0.42286E+06,
        0.60216E+06,     0.72561E+06,     0.40220E+06,     0.29904E+06,     0.18549E+06,
        0.10412E+06,      62754.    ,      33954.    ,      16418.    ,      13641.    ,
        5401.7    ,
            ];
    eilag =    [
        0.38208E+06,     0.38208E+06,     0.38208E+06,     0.38208E+06,     0.38208E+06,
        0.38208E+06,     0.38208E+06,     0.38208E+06,     0.61903E+06,     0.61903E+06,
        0.61903E+06,     0.61903E+06,     0.61903E+06,     0.61903E+06,     0.32572E+07,
        0.32572E+07,     0.32572E+07,     0.32572E+07,     0.32572E+07,     0.32572E+07,
        0.32572E+07,     0.57986E+07,     0.57986E+07,     0.57986E+07,     0.57986E+07,
        0.57986E+07,     0.57986E+07,     0.57986E+07,     0.57986E+07,     0.57986E+07,
        0.57986E+07,     0.57986E+07,     0.58097E+07,     0.58097E+07,     0.58097E+07,
        0.58097E+07,     0.58097E+07,     0.58384E+07,     0.58384E+07,     0.58384E+07,
        0.58384E+07,     0.58384E+07,     0.58384E+07,     0.58396E+07,     0.58396E+07,
        0.58396E+07,     0.56133E+07,     0.56133E+07,     0.56133E+07,     0.48434E+07,
        0.48434E+07,     0.48434E+07,     0.49519E+07,     0.43208E+07,     0.43202E+07,
        0.38564E+07,     0.37748E+07,     0.37748E+07,     0.37748E+07,     0.37748E+07,
        0.35574E+07,     0.35574E+07,     0.36063E+07,     0.36913E+07,     0.36913E+07,
        0.36913E+07,     0.36913E+07,     0.29102E+07,     0.29102E+07,     0.29102E+07,
        0.30011E+07,     0.59901E+07,     0.99958E+07,     0.90421E+07,     0.99946E+07,
        0.14233E+08,     0.17150E+08,     0.95062E+07,     0.78795E+07,     0.48875E+07,
        0.27434E+07,     0.27496E+07,     0.14877E+07,     0.71936E+06,     0.82031E+06,
        0.32483E+06,
            ];
    # Axial stiffness
    ea =       [
        0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,
        0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,
        0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,
        0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,
        0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,
        0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,
        0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,
        0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,
        0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,
        0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,     0.10000E+09,
        0.10000E+09,     0.10000E+09,     0.10000E+09,     0.93410E+08,     0.93404E+08,
        0.88248E+08,     0.88248E+08,     0.88248E+08,     0.88248E+08,     0.88248E+08,
        0.88248E+08,     0.88248E+08,     0.88852E+08,     0.89893E+08,     0.89893E+08,
        0.89893E+08,     0.89893E+08,     0.89893E+08,     0.89893E+08,     0.89893E+08,
        0.91286E+08,     0.12897E+09,     0.16660E+09,     0.16662E+09,     0.17518E+09,
        0.20904E+09,     0.22947E+09,     0.17084E+09,     0.17081E+09,     0.13452E+09,
        0.10079E+09,     0.10076E+09,     0.74117E+08,     0.51539E+08,     0.51521E+08,
        0.32421E+08,
            ];
    # Torsion stiffness
    gj =       [
        0.69444E+06,     0.69444E+06,     0.69444E+06,     0.69444E+06,     0.69444E+06,
        0.69444E+06,     0.69444E+06,     0.69444E+06,     0.48833E+06,     0.48833E+06,
        0.48833E+06,     0.48833E+06,     0.48833E+06,     0.48833E+06,     0.17976E+06,
        0.17976E+06,     0.17976E+06,     0.17976E+06,     0.17976E+06,     0.17976E+06,
        0.17976E+06,     0.17976E+06,     0.17976E+06,     0.16882E+06,     0.16882E+06,
        0.16882E+06,     0.16882E+06,     0.16882E+06,     0.16882E+06,     0.16882E+06,
        0.16882E+06,     0.16882E+06,     0.16882E+06,     0.16882E+06,     0.17058E+06,
        0.17058E+06,     0.17058E+06,     0.17058E+06,     0.17058E+06,     0.17058E+06,
        0.17208E+06,     0.17208E+06,     0.17208E+06,     0.17208E+06,     0.17208E+06,
        0.17208E+06,     0.17208E+06,     0.17208E+06,     0.17208E+06,     0.17208E+06,
        0.17208E+06,     0.17208E+06,     0.17208E+06,     0.15015E+06,     0.15013E+06,
        0.13401E+06,     0.13401E+06,     0.13401E+06,     0.13337E+06,     0.13337E+06,
        0.13337E+06,     0.13337E+06,     0.13520E+06,     0.13839E+06,     0.13839E+06,
        0.13642E+06,     0.13642E+06,     0.13642E+06,     0.13642E+06,     0.13642E+06,
        0.14068E+06,     0.28079E+06,     0.46856E+06,     0.46868E+06,     0.51805E+06,
        0.73772E+06,     0.88895E+06,     0.49273E+06,     0.49253E+06,     0.30550E+06,
        0.17148E+06,     0.17140E+06,      92738.    ,      44843.    ,      44813.    ,
        17745.    ,
            ];

    ref_bp_funcs['ea'] = muf.InterpolationFunction(rprop, ea)
    ref_bp_funcs['gj'] = muf.InterpolationFunction(rprop, gj)
    ref_bp_funcs['ei22'] = muf.InterpolationFunction(rprop, eiflap)
    ref_bp_funcs['ei33'] = muf.InterpolationFunction(rprop, eilag)

    return ref_bp_funcs



# def calcRelDiff(response_name, cs_data, *args, **kwargs):
#     bp_name = args[0]
#     target = args[1]

#     value = outputs[bp_name]
#     xo2_le = -1.0 * cs_data['chord'] * cs_data['oa2']

#     if 'sc2_le_diff' in response_name:
#         value += xo2_le
#     elif 'mc2_le_diff' in response_name:
#         value += xo2_le

#     rv = (value - target) / target

#     return rv


