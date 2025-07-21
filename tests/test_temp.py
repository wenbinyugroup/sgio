from sgio import (
    read,
    readOutputState,
    addCellDictDataToMesh,
    write,
    configure_logging,
    logger,
    )
from sgio.iofunc.gmsh import write_element_node_data

configure_logging(fout_level='debug')

fn_in = 'files/swiftcomp/sg31t_hex20_sc21.sg'
ff_in = 'sc'
# sgdim = _case['sgdim']
# model_type = _case['model_type']
# version_in = _case['version_in']
# num_cases = _case.get('num_cases', 1)
# logger.info(f'num_cases: {num_cases}')

# Read the cross-section model
sg = read(
    fn_in,
    ff_in,
    sgdim=3,
    model_type='bm2'
    )

# Read the output state
state_cases = readOutputState(
    fn_in,
    ff_in,
    'd',
    extension='sn',
    sg=sg,
    tool_version='2.1',
    num_cases=1,
    output_format=1
    )
logger.info(state_cases)
logger.info(f'{len(state_cases)} state cases')

# # Add data to the mesh
# for j, state_case in enumerate(state_cases):
#     logger.info(f'state case {j+1}')
#     # Element strain in global coordinate
#     _name = [f'case{j+1}_{name}' for name in name_e]
#     addCellDictDataToMesh(_name, state_case.getState('ee').data, sg.mesh)
#     # Element strain in material coordinate
#     _name = [f'case{j+1}_{name}' for name in name_em]
#     addCellDictDataToMesh(_name, state_case.getState('eem').data, sg.mesh)
#     # Element stress in global coordinate
#     _name = [f'case{j+1}_{name}' for name in name_s]
#     addCellDictDataToMesh(_name, state_case.getState('es').data, sg.mesh)
#     # Element stress in material coordinate
#     _name = [f'case{j+1}_{name}' for name in name_sm]
#     addCellDictDataToMesh(_name, state_case.getState('esm').data, sg.mesh)

# if 'fn_out' in _case.keys():
fn_out = '_temp/sg31t_hex20_sc21.msh'
ff_out = 'gmsh'
format_version = '4.1'

# Write the mesh to a file
write(sg, fn_out, ff_out, format_version=format_version)


with open(fn_out, 'a') as file:

    for j, state_case in enumerate(state_cases):
        for _name, _state in state_case.states.items():
            write_element_node_data(file, _state.label[0], _state.data)
            # file.write('$ElementNodeData\n')

            # _data = _state.data

            # # string tags
            # file.write('1\n')
            # file.write(f'"{_state.label[0]}"\n')

            # # real tags
            # file.write('1\n')
            # file.write('0.0\n')

            # # integer tags
            # file.write('3\n')
            # file.write('0\n')  # time step
            # file.write('1\n')  # number of components
            # file.write(f'{len(_data)}\n')  # number of elements

            # for _eid, _nvals in _data.items():
            #     file.write(f'{_eid} {len(_nvals)}')
            #     for _v in _nvals:
            #         file.write(f'  {_v}')
            #     file.write('\n')

            # file.write('$EndElementNodeData\n')
