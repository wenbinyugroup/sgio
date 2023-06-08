# import sys
# import csv
import numpy as np
import pandas as pd


def calDirectionCosine(base0, base1):
    r"""
    b = [
        [b11, b12, b13],
        [b21, b22, b23],
        [b31, b32, b33]
    ]
    """
    c = np.zeros((3, 3))

    for i in range(3):
        for j in range(3):
            c[i, j] = np.dot(base1[i], base0[j]) / (np.linalg.norm(base1[i]) * np.linalg.norm(base0[j]))

    return c


def calcGlobalResponse(frame_b, frame_d, u_g, f_g, m_g):

    base_g = np.eye(3)

    xb = frame_b[0] / np.linalg.norm(frame_b[0])
    yb = frame_b[1] / np.linalg.norm(frame_b[1])
    zb = frame_b[2] / np.linalg.norm(frame_b[2])
    base_b = np.array([xb, yb, zb])

    xd = frame_d[0] / np.linalg.norm(frame_d[0])
    yd = frame_d[1] / np.linalg.norm(frame_d[1])
    zd = frame_d[2] / np.linalg.norm(frame_d[2])
    base_d = np.array([xd, yd, zd])

    c_bd = calDirectionCosine(base_b, base_d)
    c_gd = calDirectionCosine(base_g, base_d)

    u_d = np.dot(c_gd, u_g)
    f_d = np.dot(c_gd, f_g)
    m_d = np.dot(c_gd, m_g)

    return u_d.tolist(), c_bd.tolist(), f_d.tolist(), m_d.tolist()


def main(fn_undeform, ls_fn_deform, fn_out, conds, cond_keys, loc_key='node_id'):
    r"""
    """
    ls_resp_cases = []

    ls_resp_keys = [loc_key,]
    if isinstance(cond_keys, str):
        ls_resp_keys.append(cond_keys)
    elif isinstance(cond_keys, list):
        ls_resp_keys.extend(cond_keys)
    ls_resp_keys.extend(['u1', 'u2', 'u3'])
    ls_resp_keys.extend(['c11', 'c12', 'c13', 'c21', 'c22', 'c23', 'c31', 'c32', 'c33'])
    ls_resp_keys.extend(['f1', 'f2', 'f3'])
    ls_resp_keys.extend(['m1', 'm2', 'm3'])

    df_ud_raw = pd.read_csv(fn_undeform, index_col=loc_key)

    for i, fn_deform in enumerate(ls_fn_deform):
        df_de_raw = pd.read_csv(fn_deform, index_col=loc_key)

        _cond = conds[i]

        for index, row_ud in df_ud_raw.iterrows():
            _resp = [index,]
            if isinstance(_cond, list):
                _resp.extend(_cond)
            else:
                _resp.append(_cond)

            xb = row_ud[['local_x:0', 'local_x:1', 'local_x:2']].values
            yb = row_ud[['local_y:0', 'local_y:1', 'local_y:2']].values
            zb = row_ud[['local_z:0', 'local_z:1', 'local_z:2']].values

            row_de = df_de_raw.loc[index]
            xd = row_de[['local_x:0', 'local_x:1', 'local_x:2']].values
            yd = row_de[['local_y:0', 'local_y:1', 'local_y:2']].values
            zd = row_de[['local_z:0', 'local_z:1', 'local_z:2']].values

            u_g = row_de[['coords_a:0', 'coords_a:1', 'coords_a:2']].values - row_ud[['coords_a:0', 'coords_a:1', 'coords_a:2']].values
            f_g = row_de[['app_forces:0', 'app_forces:1', 'app_forces:2']].values + row_de[['gravity_forces:0', 'gravity_forces:1', 'gravity_forces:2']].values
            m_g = row_de[['app_moments:0', 'app_moments:1', 'app_moments:2']].values + row_de[['gravity_moments:0', 'gravity_moments:1', 'gravity_moments:2']].values

            u, c, f, m = calcGlobalResponse(
                [xb, yb, zb], [xd, yd, zd], u_g, f_g, m_g
            )

            _resp.extend(u)
            _resp.extend(c[0])
            _resp.extend(c[1])
            _resp.extend(c[2])
            _resp.extend(f)
            _resp.extend(m)

            ls_resp_cases.append(_resp)

    df = pd.DataFrame(np.array(ls_resp_cases), columns=ls_resp_keys)
    df[loc_key] = df[loc_key].astype(int)
    df.to_csv(fn_out, index=False)

    return


def convertGlobalResponseFileFormat(data, name, logger, *args, **kwargs):

    # print(kwargs)

    main(
        kwargs['undeform_data'],
        kwargs['deformed_data'],
        kwargs['output_file'],
        kwargs['conditions'],
        kwargs['condition_tags'],
        kwargs['location_tag']
    )

    return



if __name__ == '__main__':
    # fn_data_undeform = sys.argv[1]
    # fn_data_deform = sys.argv[2]
    # nid = int(sys.argv[3])
    # fn_global = sys.argv[4]

    fn_undeform = 'undeformed.csv'

    ls_fn_deform = [
        'config_a_aoa_2_1mm_data.csv',
        'config_a_aoa_5_1mm_data.csv',
        'config_a_aoa_8_1mm_data.csv'
    ]

    conds = [
        [2,], [5,], [8,]
    ]

    cond_keys = ['aoa',]

    node_key = 'node_id'

    fn_out = 'test.csv'

    main(fn_undeform, ls_fn_deform, fn_out, conds, cond_keys, node_key)

    # u, c, f, m, = getCSGlobalInput(fn_data_undeform, fn_data_deform, nid)

    # with open(fn_global, 'w') as file:
    #     writeCSGlobalInput(file, u, c, f, m)

