"""Generate ``docs/source/examples/<name>.md`` from ``examples/<name>/README.md``.

The example README is the single source of truth. This module rewrites it into a
MyST page: relative paths are repointed at the example folder, ``<!-- code: f -->``
markers become ``literalinclude`` directives and markdown images become ``figure``
directives.

A generated page carries :data:`HEADER`. Pages without it are hand-written and are
never touched, so examples can be migrated one at a time.
"""

from __future__ import annotations

import re
from pathlib import Path

#: Marker identifying a generated page.
HEADER = '<!-- Generated from {source}. Do not edit; edit the README instead. -->\n\n'

#: ``<!-- code: run.py -->`` -- insert a source listing here.
RE_CODE = re.compile(r'^<!--[ \t]*code:[ \t]*(\S+?)[ \t]*-->[ \t]*$', re.MULTILINE)

#: ``![alt](image.png "60%")`` on its own line -- render as a numbered figure.
#: The optional title sets the figure width; it is a tooltip on GitHub.
RE_FIGURE = re.compile(
    r'^!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)(?:[ \t]+"(?P<width>[^"]*)")?\)[ \t]*$',
    re.MULTILINE)

#: Any remaining inline link or image target.
RE_LINK = re.compile(r'(?<=\]\()(?P<target>[^)]+)(?=\))')

#: File extension -> Pygments lexer, for ``literalinclude``.
LANGUAGES = {'.py': 'python', '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml'}

#: Figure width when the image carries no title.
DEFAULT_WIDTH = '80%'

#: An ``examples`` subfolder is an example only if it holds a runnable script.
RUN_SCRIPT = 'run*.py'


def _is_local(target: str) -> bool:
    """Return whether a link target points at a file next to the README."""
    return not (target.startswith(('http://', 'https://', '#', '/')) or ':' in target)


def convert(text: str, name: str) -> str:
    """Convert one example README into the body of a MyST page.

    Parameters
    ----------
    text : str
        Contents of ``examples/<name>/README.md``.
    name : str
        Example folder name, used to build paths relative to the page.

    Returns
    -------
    str
        The MyST page body, without :data:`HEADER`.
    """
    prefix = f'../../../examples/{name}/'

    def _code(match: re.Match) -> str:
        src = match.group(1)
        language = LANGUAGES.get(Path(src).suffix, 'text')
        return (f'```{{literalinclude}} {prefix}{src}\n'
                f':language: {language}\n'
                '```')

    def _figure(match: re.Match) -> str:
        src = match.group('src')
        target = prefix + src if _is_local(src) else src
        alt = match.group('alt')
        caption = f'\n{alt}\n' if alt else ''
        return (f'```{{figure}} {target}\n'
                ':align: center\n'
                f':width: {match.group("width") or DEFAULT_WIDTH}\n{caption}'
                '```')

    # Order matters: figures are consumed before the generic link rewrite.
    text = RE_CODE.sub(_code, text)
    text = RE_FIGURE.sub(_figure, text)
    return RE_LINK.sub(
        lambda m: prefix + m.group('target') if _is_local(m.group('target')) else m.group('target'),
        text,
    )


def _hand_written_examples(out_dir: Path) -> set[str]:
    """Return the examples covered by hand-written pages.

    A hand-written page may carry any file name and may draw on several example
    folders, so ownership is read from the paths it references rather than from
    its name.

    Parameters
    ----------
    out_dir : Path
        The ``docs/source/examples`` directory.

    Returns
    -------
    set of str
        Example folder names that a hand-written page already documents.
    """
    claimed = set()

    for page in out_dir.glob('*.*'):
        text = page.read_text(encoding='utf-8')
        if text.startswith('<!-- Generated from'):
            continue
        claimed.update(re.findall(r'examples/([A-Za-z0-9_]+)/', text))

    return claimed


def generate(root: Path) -> list[str]:
    """Regenerate every migrated example page under ``docs/source/examples``.

    Parameters
    ----------
    root : Path
        Repository root, containing both ``examples`` and ``docs``.

    Returns
    -------
    list of str
        Names of the examples whose page was written.
    """
    out_dir = root / 'docs' / 'source' / 'examples'
    claimed = _hand_written_examples(out_dir)
    written = []

    for readme in sorted((root / 'examples').glob('*/README.md')):
        name = readme.parent.name
        page = out_dir / f'{name}.md'

        # A folder without a runnable script is not an example.
        if not any(readme.parent.glob(RUN_SCRIPT)):
            continue

        # Own a page only once it carries the header; never adopt a hand-written
        # one, and never add a second page for an example a hand-written page
        # already documents under another name.
        if page.exists():
            if not page.read_text(encoding='utf-8').startswith('<!-- Generated from'):
                continue
        elif name in claimed:
            continue

        body = readme.read_text(encoding='utf-8').strip()
        if not body:
            continue

        header = HEADER.format(source=f'examples/{name}/README.md')
        page.write_text(header + convert(body, name) + '\n', encoding='utf-8')
        written.append(name)

    return written


if __name__ == '__main__':
    for example in generate(Path(__file__).resolve().parents[1]):
        print(f'generated docs/source/examples/{example}.md')
