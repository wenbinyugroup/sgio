from __future__ import annotations

from typing import Optional

from ._deprecations import warn_model_deprecation


class SectionResponse():
    """Generalized stress/strain for an SG model."""

    def __init__(self):
        warn_model_deprecation('SectionResponse')
        self.displacement: list = [0, 0, 0]
        self.directional_cosine: list = [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ]
        self.load_type: int = 0
        self.load_tags = []
        self.load: list = []
        self.loc: dict = {}
        self.cond: dict = {}
        self.distr_load = [0, 0, 0, 0, 0, 0]
        self.distr_load_d1 = [0, 0, 0, 0, 0, 0]
        self.distr_load_d2 = [0, 0, 0, 0, 0, 0]
        self.distr_load_d3 = [0, 0, 0, 0, 0, 0]

    def getDisplacement(self):
        return self.displacement

    def getDirectionCosine(self):
        return self.directional_cosine

    def getLoad(self):
        return self.load

    def getDistributedLoad(self):
        return [
            self.distr_load,
            self.distr_load_d1,
            self.distr_load_d2,
            self.distr_load_d3
        ]

    def strU(self, float_format='16.6e', delimiter=','):
        fstr = '{:' + float_format + '}'
        return delimiter.join([fstr.format(u) for u in self.displacement])

    def strC(self, float_format='16.6e', col_delimiter=',', row_delimiter=','):
        fstr = '{:' + float_format + '}'
        return row_delimiter.join(
            [(col_delimiter.join(
                [fstr.format(c) for c in row]
            )) for row in self.directional_cosine]
        )

    def strS(self, float_format='16.6e', delimiter=','):
        fstr = '{:' + float_format + '}'
        return delimiter.join([fstr.format(s) for s in self.load])

    def __repr__(self):
        lines = ['Displacement', ]
        lines.append('\n'.join(['  u{} = {:16.6e}'.format(i + 1, u) for i, u in enumerate(self.displacement)]))
        lines.append('Rotation (directional cosine)')
        lines.append('\n'.join(
            [('  ' + ', '.join(
                ['c{}{} = {:16.6e}'.format(i + 1, j + 1, c) for j, c in enumerate(row)]
            )) for i, row in enumerate(self.directional_cosine)]
        ))
        lines.append('Load')
        lines.append('\n'.join(['  {} = {:16.6e}'.format(t, s) for t, s in zip(self.load_tags, self.load)]))
        return '\n'.join(lines)

    def writeSGInputGlbU(self, file, float_format='16.6e'):
        """Compatibility wrapper around ``iofunc.common.response_writers``."""
        warn_model_deprecation('SectionResponse.writeSGInputGlbU')
        from ..iofunc.common.response_writers import write_section_response_displacement

        write_section_response_displacement(file, self.displacement, float_format)

    def writeSGInputGlbC(self, file, float_format='16.6e'):
        """Compatibility wrapper around ``iofunc.common.response_writers``."""
        warn_model_deprecation('SectionResponse.writeSGInputGlbC')
        from ..iofunc.common.response_writers import write_section_response_rotation

        write_section_response_rotation(file, self.directional_cosine, float_format)

    def writeSGInputGlbS(self, file, file_format, int_format='8d', float_format='16.6e'):
        """Compatibility wrapper around ``iofunc.common.response_writers``."""
        warn_model_deprecation('SectionResponse.writeSGInputGlbS')
        from ..iofunc.common.response_writers import write_section_response_load

        write_section_response_load(
            file=file,
            load=self.load,
            file_format=file_format,
            load_type=self.load_type,
            distributed_loads=[
                self.distr_load,
                self.distr_load_d1,
                self.distr_load_d2,
                self.distr_load_d3,
            ],
            int_format=int_format,
            float_format=float_format,
        )


class StructureResponseCase():
    """Legacy case wrapper for sectional response payloads."""

    def __init__(
        self,
        loc: Optional[dict] = None,
        cond: Optional[dict] = None,
        response: Optional[SectionResponse] = None,
    ):
        warn_model_deprecation('StructureResponseCase')
        self._loc_tags = []
        self._loc_values = []
        self._cond_tags = []
        self._cond_values = []
        self._response: Optional[SectionResponse] = response

        if loc is not None:
            for tag, value in loc.items():
                self._loc_tags.append(tag)
                self._loc_values.append(value)

        if cond is not None:
            for tag, value in cond.items():
                self._cond_tags.append(tag)
                self._cond_values.append(value)

    @property
    def loc(self) -> dict:
        """Return location tags and values as a dictionary."""
        return dict(zip(self._loc_tags, self._loc_values))

    @property
    def cond(self) -> dict:
        """Return condition tags and values as a dictionary."""
        return dict(zip(self._cond_tags, self._cond_values))

    @property
    def response(self) -> Optional[SectionResponse]:
        """Return the sectional response payload."""
        return self._response

    @response.setter
    def response(self, value: Optional[SectionResponse]) -> None:
        self._response = value

    def __repr__(self):
        lines = []
        lines.append('Location:')
        for t, v in zip(self._loc_tags, self._loc_values):
            lines.append(f'  {t} = {v}')
        lines.append('Condition:')
        for t, v in zip(self._cond_tags, self._cond_values):
            lines.append(f'  {t} = {v}')
        lines.append(str(self._response))
        return '\n'.join(lines)

    def getLocation(self, tag):
        """Get a location value by tag."""
        value = None
        for _t, _v in zip(self._loc_tags, self._loc_values):
            if tag == _t:
                value = _v
                break
        return value

    def getCondition(self, tag):
        """Get a condition value by tag."""
        value = None
        for _t, _v in zip(self._cond_tags, self._cond_values):
            if tag == _t:
                value = _v
                break
        return value

    def getLocationOrCondition(self, tag):
        """Get a location or condition value by tag."""
        value = self.getLocation(tag)
        if value is None:
            value = self.getCondition(tag)
        return value

    def __contains__(self, key: str) -> bool:
        """Support legacy dictionary-style membership checks."""
        if key == 'response':
            return True
        return key in self._loc_tags or key in self._cond_tags

    def __getitem__(self, key: str):
        """Support legacy dictionary-style access."""
        if key == 'response':
            return self._response

        if key in self._loc_tags:
            return self.getLocation(key)
        if key in self._cond_tags:
            return self.getCondition(key)

        raise KeyError(key)


class StructureResponseCases():
    """Cases of generalized stress/strain."""

    def __init__(self):
        warn_model_deprecation('StructureResponseCases')
        self.loc_tags = []
        self.cond_tags = []
        self.responses: list[StructureResponseCase] = []

    def __repr__(self):
        lines = []
        for _resp in self.responses:
            _resp = self._coerce_response_case(_resp)
            lines.append('-' * 20)
            lines.append(str(_resp))
        lines.append('-' * 20)
        return '\n'.join(lines)

    def getResponsesByLocCond(self, **kwargs):
        """Get response by providing location and condition."""
        resps = []

        for _resp in self.responses:
            _resp = self._coerce_response_case(_resp)
            found = True
            for _k, _v in kwargs.items():
                if _v != _resp.getLocationOrCondition(_k):
                    found = False
                    break
            if found:
                resps.append(_resp)

        return resps

    def _coerce_response_case(self, resp) -> StructureResponseCase:
        """Convert legacy dictionary payloads to ``StructureResponseCase``."""
        if isinstance(resp, StructureResponseCase):
            return resp

        if isinstance(resp, dict):
            loc = {tag: resp[tag] for tag in self.loc_tags if tag in resp}
            cond = {tag: resp[tag] for tag in self.cond_tags if tag in resp}
            response = resp.get('response')
            return StructureResponseCase(loc=loc, cond=cond, response=response)

        raise TypeError(
            f'response case must be StructureResponseCase or dict, got {type(resp)}'
        )

    def addResponseCase(self, loc, cond, sect_resp: SectionResponse):
        """Add a legacy response case."""
        resp_case = StructureResponseCase(
            loc={_tag: _value for _tag, _value in zip(self.loc_tags, loc)},
            cond={_tag: _value for _tag, _value in zip(self.cond_tags, cond)},
            response=sect_resp,
        )
        self.responses.append(resp_case)


__all__ = ['SectionResponse', 'StructureResponseCase', 'StructureResponseCases']
