from sgio.meshio._mesh import Mesh

def addCellDictDataToMesh(name:str|list, dict_data:dict[int, list], mesh:Mesh):
    """Add cell/element data (dictionary) to cell_data of mesh.

    The mesh should contain a map between (cell_type, index) and element id.    

    Parameters:
    -----------
    name:
        Name(s) of the cell data. If it is a list, then it should have the same length as data list for each element.
    dict_data:
        Data in the dictionary form {eid: data}.
    mesh:
        Mesh where the cell data will be added.

    """

    _cell_data_eid = mesh.cell_data['element_id']

    if isinstance(name, str):
        _cell_data = []

        for _i, _typei_ids in enumerate(_cell_data_eid):
            _typei_data = []

            for _j, _eid in enumerate(_typei_ids):
                _data = dict_data[_eid]
                _typei_data.append(_data)

            _cell_data.append(_typei_data)

        mesh.cell_data[name] = _cell_data


    elif isinstance(name, list):
        ncomps = len(name)
        _cell_data_all = []
        for _i in range(ncomps):
            _cell_data_all.append([])

        for _i, _typei_ids in enumerate(_cell_data_eid):
            _typei_data_all = []
            for _ in range(ncomps):
                _typei_data_all.append([])

            for _j, _eid in enumerate(_typei_ids):
                _data_all = dict_data[_eid]
                for _k, _data in enumerate(_data_all):
                    _typei_data_all[_k].append(_data)

            for _l in range(ncomps):
                _cell_data_all[_l].append(_typei_data_all[_l])

        for _i, _name in enumerate(name):
            _data = _cell_data_all[_i]
            mesh.cell_data[_name] = _data

    return
