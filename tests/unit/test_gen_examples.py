"""Tests for the example README -> MyST page conversion."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2] / 'docs'))

from gen_examples import convert, generate  # noqa: E402


@pytest.mark.unit
class TestConvert:
    """Conversion of README markdown into MyST directives."""

    def test_code_marker_becomes_literalinclude(self):
        # Arrange
        text = '<!-- code: run.py -->'

        # Act
        result = convert(text, 'demo')

        # Assert
        assert '```{literalinclude} ../../../examples/demo/run.py' in result
        assert ':language: python' in result

    def test_image_becomes_figure_with_rewritten_path(self):
        # Arrange
        text = '![mesh](pyvista.png)'

        # Act
        result = convert(text, 'demo')

        # Assert
        assert '```{figure} ../../../examples/demo/pyvista.png' in result
        assert ':align: center' in result

    def test_local_link_is_rewritten(self):
        # Arrange
        text = '- [run.py](run.py): the script'

        # Act
        result = convert(text, 'demo')

        # Assert
        assert result == '- [run.py](../../../examples/demo/run.py): the script'

    def test_external_and_anchor_links_are_untouched(self):
        # Arrange
        text = '[docs](https://example.com) and [top](#intro)'

        # Act
        result = convert(text, 'demo')

        # Assert
        assert result == text

    def test_myst_roles_pass_through(self):
        # Arrange
        text = 'See {func}`sgio.read` and {doc}`/ref/sg_manifest`.'

        # Act
        result = convert(text, 'demo')

        # Assert
        assert result == text


@pytest.mark.unit
class TestGenerate:
    """Ownership rules for pages under docs/source/examples."""

    @staticmethod
    def _make_repo(root: Path, readme: str) -> Path:
        example = root / 'examples' / 'demo'
        example.mkdir(parents=True)
        (example / 'run.py').write_text('', encoding='utf-8')
        (example / 'README.md').write_text(readme, encoding='utf-8')
        out_dir = root / 'docs' / 'source' / 'examples'
        out_dir.mkdir(parents=True)
        return out_dir / 'demo.md'

    def test_writes_page_with_header(self, tmp_path):
        # Arrange
        page = self._make_repo(tmp_path, '# Demo\n')

        # Act
        written = generate(tmp_path)

        # Assert
        assert written == ['demo']
        assert page.read_text(encoding='utf-8').startswith('<!-- Generated from')

    def test_skips_hand_written_page(self, tmp_path):
        # Arrange
        page = self._make_repo(tmp_path, '# Demo\n')
        page.write_text('# Hand written\n', encoding='utf-8')

        # Act
        written = generate(tmp_path)

        # Assert
        assert written == []
        assert page.read_text(encoding='utf-8') == '# Hand written\n'

    def test_skips_empty_readme(self, tmp_path):
        # Arrange
        page = self._make_repo(tmp_path, '')

        # Act
        written = generate(tmp_path)

        # Assert
        assert written == []
        assert not page.exists()

    def test_skips_folder_without_run_script(self, tmp_path):
        # Arrange
        page = self._make_repo(tmp_path, '# Demo\n')
        (tmp_path / 'examples' / 'demo' / 'run.py').unlink()

        # Act
        written = generate(tmp_path)

        # Assert
        assert written == []
        assert not page.exists()

    def test_skips_example_claimed_by_hand_written_page(self, tmp_path):
        # Arrange
        page = self._make_repo(tmp_path, '# Demo\n')
        other = page.parent / 'other_name.md'
        other.write_text('See ../../../examples/demo/run.py\n', encoding='utf-8')

        # Act
        written = generate(tmp_path)

        # Assert
        assert written == []
        assert not page.exists()

    def test_blank_line_after_a_directive_is_kept(self, tmp_path):
        # Arrange
        page = self._make_repo(tmp_path, '<!-- code: run.py -->\n\nNext paragraph.\n')

        # Act
        generate(tmp_path)

        # Assert
        assert page.read_text(encoding='utf-8').endswith('```\n\nNext paragraph.\n')

    def test_image_title_sets_figure_width(self, tmp_path):
        # Arrange
        page = self._make_repo(tmp_path, '![](preview.png "70%")\n')

        # Act
        generate(tmp_path)

        # Assert
        assert ':width: 70%' in page.read_text(encoding='utf-8')
