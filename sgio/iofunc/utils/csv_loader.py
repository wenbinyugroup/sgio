"""CSV file loading utilities for Structure Gene data.

This module provides functions for reading load data from CSV files.
"""

from __future__ import annotations

import csv
import logging

import sgio.model as sgmodel


logger = logging.getLogger(__name__)


def read_load_csv(
    fn: str, smdim: int, model: str | int, load_tags: list = [],
    load_type: int = 0, disp_tags: list = ['u1', 'u2', 'u3'],
    rot_tags: list = ['c11', 'c12', 'c13', 'c21', 'c22', 'c23', 'c31', 'c32', 'c33'],
    loc_tags: list = ['loc',], cond_tags: list = [],
    loc_vtypes: list = [], cond_vtypes: list = [],
    delimiter: str = ',', nhead: int = 1, encoding: str = 'utf-8-sig'
) -> list[sgmodel.StateCase]:
    """Read a CSV file containing load data for a given structure.
    
    The file should have the following format:
    
    loc, cond, u1, u2, u3, c11, c12, c13, c21, c22, c23, c31, c32, c33, f1, f2, ...
    1, 1, 1, 2, 3, 0, 0, 1, 0, 1, 0, 0, 0, 1, 4, 5, ...
    
    Parameters
    ----------
    fn : str
        The filename of the CSV file to read.
    smdim : int
        The dimension of the structure model.
    model : str or int
        The model type of the structure.
    load_tags : list, optional
        The tags of the loads to be read. Defaults to an empty list.
    load_type : int, optional
        The type of the loads. Defaults to 0.
    disp_tags : list, optional
        The tags of the displacements to be read. Defaults to ['u1', 'u2', 'u3'].
    rot_tags : list, optional
        The tags of the rotations to be read. Defaults to ['c11', 'c12', 'c13', 'c21', 'c22', 'c23', 'c31', 'c32', 'c33'].
    loc_tags : list, optional
        The tags of the locations to be read. Defaults to ['loc',].
    cond_tags : list, optional
        The tags of the conditions to be read. Defaults to an empty list.
    loc_vtypes : list, optional
        The value types of the locations to be read. Defaults to an empty list.
    cond_vtypes : list, optional
        The value types of the conditions to be read. Defaults to an empty list.
    delimiter : str, optional
        The delimiter of the CSV file. Defaults to ','.
    nhead : int, optional
        The number of header lines to skip. Defaults to 1.
    encoding : str, optional
        The encoding of the CSV file. Defaults to 'utf-8-sig'.
    
    Returns
    -------
    list[StateCase]
        State cases read from the CSV file. Each case stores location and
        condition metadata in ``StateCase.case`` and the macro response fields
        in ``StateCase.states``.
    """
    
    if len(load_tags) == 0:
        if smdim == 1:
            if model == 'b1':
                load_tags = ['f1', 'm1', 'm2', 'm3']
            elif model == 'b2':
                load_tags = ['f1', 'f2', 'f3', 'm1', 'm2', 'm3']
    
    if isinstance(loc_tags, str):
        loc_tags = [loc_tags,]
    if isinstance(cond_tags, str):
        cond_tags = [cond_tags,]
    
    if isinstance(loc_vtypes, str):
        loc_vtypes = [loc_vtypes,]
    if isinstance(cond_vtypes, str):
        cond_vtypes = [cond_vtypes,]
    
    if len(loc_vtypes) < len(loc_tags):
        if len(loc_vtypes) == 0:
            loc_vtypes = ['int',] * len(loc_tags)
        elif len(loc_vtypes) == 1:
            loc_vtypes = loc_vtypes * len(loc_tags)
    if len(cond_vtypes) < len(cond_tags):
        if len(cond_vtypes) == 0:
            cond_vtypes = ['int',] * len(cond_tags)
        elif len(cond_vtypes) == 1:
            cond_vtypes = cond_vtypes * len(cond_tags)
    
    state_cases: list[sgmodel.StateCase] = []
    
    with open(fn, 'r', encoding=encoding) as file:
        cr = csv.reader(file, delimiter=delimiter)
        
        tags_idx = {}
        
        hi = 0
        for i, row in enumerate(cr):
            row = [s.strip() for s in row]
            if row[0] == '':
                continue
            
            if i < nhead:
                if hi == 0:
                    for tag in loc_tags:
                        if tag not in row:
                            raise ValueError(f'Column {tag} not found in the file')
                        tags_idx[tag] = row.index(tag)
                    for tag in cond_tags:
                        if tag not in row:
                            raise ValueError(f'Column {tag} not found in the file')
                        tags_idx[tag] = row.index(tag)
                    for tag in disp_tags:
                        if tag not in row:
                            raise ValueError(f'Column {tag} not found in the file')
                        tags_idx[tag] = row.index(tag)
                    for tag in rot_tags:
                        if tag not in row:
                            raise ValueError(f'Column {tag} not found in the file')
                        tags_idx[tag] = row.index(tag)
                    for tag in load_tags:
                        if tag not in row:
                            raise ValueError(f'Column {tag} not found in the file')
                        tags_idx[tag] = row.index(tag)
                hi += 1
                continue
            
            else:
                case_data = {'load_type': load_type}

                for tag, vtype in zip(loc_tags, loc_vtypes):
                    value = eval(vtype)(row[tags_idx[tag]])
                    case_data[tag] = value

                for tag, vtype in zip(cond_tags, cond_vtypes):
                    value = eval(vtype)(row[tags_idx[tag]])
                    case_data[tag] = value

                load = [float(row[tags_idx[tag]]) for tag in load_tags]
                displacement = [float(row[tags_idx[tag]]) for tag in disp_tags]
                rotation = [
                    [float(row[tags_idx[tag]]) for tag in rot_tags[0:3]],
                    [float(row[tags_idx[tag]]) for tag in rot_tags[3:6]],
                    [float(row[tags_idx[tag]]) for tag in rot_tags[6:9]]
                ]

                state_case = sgmodel.StateCase(case=case_data, states={})
                state_case.addState(
                    name='displacement',
                    state=sgmodel.State(
                        name='displacement',
                        data=displacement,
                        label=disp_tags,
                    ),
                )
                state_case.addState(
                    name='rotation',
                    state=sgmodel.State(
                        name='rotation',
                        data=rotation,
                        label=rot_tags,
                    ),
                )
                state_case.addState(
                    name='load',
                    state=sgmodel.State(
                        name='load',
                        data=load,
                        label=load_tags,
                    ),
                )
                state_cases.append(state_case)

    return state_cases
