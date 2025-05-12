import os
import yaml

from sgio import (
    read,
    readOutputState,
    addCellDictDataToMesh,
    write,
    configure_logging,
    logger,
    )

configure_logging(cout_level='info')

test_case_files = [
    'test_io_vabs_out_d.yml',
]

# Base name of the VABS files
# fn_base = 'files/vabs/version_4_1/uh60a'
# model_type = 'bm2'  # bm1: Euler-Bernoulli beam, bm2: Timoshenko beam



# ver = '4.1'  # VABS version
# fn_sg = f'{fn_base}.sg'
# fn_sg_ele = f'{fn_sg}.ele'
# fn_msh = f'{fn_base}.msh'

# Component labels in visualization
# name_u = ['u1', 'u2', 'u3']
name_e = ['e11', '2e12', '2e13', 'e22', '2e23', 'e33']  # Strain in global coordinate
name_em = ['e11m', '2e12m', '2e13m', 'e22m', '2e23m', 'e33m']  # Strain in material coordinate
name_s = ['s11', '2s12', '2s13', 's22', '2s23', 's33']  # Stress in global coordinate
name_sm = ['s11m', 's12m', 's13m', 's22m', 's23m', 's33m']  # Stress in material coordinate

def test_io_vabs_out_state_d(fn_test_cases, input_dir, output_dir):

    with open(f'{input_dir}/{fn_test_cases}', 'r') as file:
        test_cases = yaml.safe_load(file)

    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for _i, _case in enumerate(test_cases):
        print()

        fn_in = f'{input_dir}/{_case["fn_in"]}'
        ff_in = _case['ff_in']
        version_in = _case['version_in']
        num_cases = _case.get('num_cases', 1)
        logger.info(f'num_cases: {num_cases}')

        # Read the cross-section model
        sg = read(fn_in, ff_in)

        # Read the output state
        state_cases = readOutputState(
            fn_in, ff_in, 'd', sg=sg, tool_version=version_in, num_cases=num_cases)
        logger.info(state_cases)
        logger.info(f'{len(state_cases)} state cases')

        # Add data to the mesh
        for j, state_case in enumerate(state_cases):
            logger.info(f'state case {j+1}')
            # Element strain in global coordinate
            _name = [f'case{j+1}_{name}' for name in name_e]
            addCellDictDataToMesh(_name, state_case.getState('ee').data, sg.mesh)
            # Element strain in material coordinate
            _name = [f'case{j+1}_{name}' for name in name_em]
            addCellDictDataToMesh(_name, state_case.getState('eem').data, sg.mesh)
            # Element stress in global coordinate
            _name = [f'case{j+1}_{name}' for name in name_s]
            addCellDictDataToMesh(_name, state_case.getState('es').data, sg.mesh)
            # Element stress in material coordinate
            _name = [f'case{j+1}_{name}' for name in name_sm]
            addCellDictDataToMesh(_name, state_case.getState('esm').data, sg.mesh)

        if 'fn_out' in _case.keys():
            fn_out = f'{output_dir}/{_case["fn_out"]}'
            ff_out = _case['ff_out']
            format_version = _case['format_version']

            # Write the mesh to a file
            write(sg, fn_out, ff_out, format_version=format_version)



if __name__ == '__main__':
    input_dir = 'files'
    output_dir = '_temp'

    for fn_test_cases in test_case_files:
        test_io_vabs_out_state_d(fn_test_cases, input_dir, output_dir)

