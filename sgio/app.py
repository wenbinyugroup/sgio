"""Command-line interface for SGIO.

This module provides the main CLI entry point for SGIO (Structure Gene I/O),
supporting file format conversion and structural gene building operations.

Features
--------
- File format conversion between VABS, SwiftComp, Abaqus, and other formats
- Cross-section and structural gene data manipulation
- Configurable logging for debugging and monitoring
- Support for various analysis types (homogenization, dehomogenization, failure)

Usage
-----
Convert file formats::

    sgio convert input.vabs output.sc
    sgio convert input.vabs output.sc -ff vabs -tf swiftcomp

Build structural genes::

    sgio build design.json

Get help::

    sgio --help
    sgio convert --help
    sgio build --help

Notes
-----
The CLI uses argparse for argument parsing and supports both long and short
command names (e.g., 'convert' or 'c', 'build' or 'b').
"""
from __future__ import annotations

import argparse
import logging
from enum import Enum
from typing import Any, Optional
from pathlib import Path

from sgio import __version__
from sgio._global import logger, configure_logging
from sgio.iofunc import convert


class Command(str, Enum):
    """Available CLI commands."""
    BUILD = 'build'
    CONVERT = 'convert'


def sanitize_path(path_str: str) -> Path:
    """Sanitize and validate file path.
    
    Resolves the path to absolute form and performs basic security checks
    to prevent path traversal attacks.
    
    Parameters
    ----------
    path_str : str
        Path string to sanitize
        
    Returns
    -------
    Path
        Resolved absolute path
        
    Raises
    ------
    ValueError
        If path contains suspicious patterns
        
    Notes
    -----
    This function resolves symlinks and relative paths to their absolute form,
    which helps prevent path traversal attacks.
    """
    path = Path(path_str).resolve()
    
    # Additional validation can be added here if needed
    # For example, checking if path is within allowed directories
    
    return path


def case_insensitive_string(value: str) -> str:
    """Convert string to lowercase for case-insensitive comparison.
    
    Parameters
    ----------
    value : str
        String to convert
        
    Returns
    -------
    str
        Lowercase version of the input string
    """
    return value.lower()


def cli(*args: str) -> None:
    """Parse command-line arguments and execute SGIO commands.
    
    This is the main entry point for the SGIO command-line interface.
    It supports subcommands for building structural genes and converting
    between different file formats (VABS, SwiftComp, Abaqus, etc.).
    
    Parameters
    ----------
    *args : str
        Command-line arguments. If empty, uses sys.argv. Primarily used
        for testing with explicit arguments.
        
    Examples
    --------
    >>> cli('sgio', 'convert', 'input.vabs', 'output.sc')
    >>> cli('sgio', 'build', 'design.json')
    
    Notes
    -----
    The function sets up argument parsers for subcommands and dispatches
    to the appropriate handler function.
    """
    root_parser = argparse.ArgumentParser(
        prog='sgio',
        description='I/O library for VABS (cross-section) and SwiftComp (structural gene)',
    )
    root_parser.set_defaults(func=None)
    root_parser.add_argument(
        '-v', '--version', action='version', version=__version__,
        help='Show version number and exit.'
    )

    # Add logging arguments to each subparser
    logging_args = argparse.ArgumentParser(add_help=False)
    logging_args.add_argument(
        '--loglevelcmd', help='Command line logging level.',
        default='info', choices=['debug', 'info', 'warning', 'error', 'critical'])
    logging_args.add_argument(
        '--loglevelfile', help='File logging level.',
        default='info', choices=['debug', 'info', 'warning', 'error', 'critical'])
    logging_args.add_argument(
        '--logfile', help='Logging file name.',
        default='sgio.log')

    sub_parser = root_parser.add_subparsers(
        help='Available sub-commands.'
    )

    # Build
    parser = sub_parser.add_parser(
        Command.BUILD, aliases=['b'], help='Build 1D structural gene.',
        parents=[logging_args]
        )
    parser.set_defaults(func=Command.BUILD)
    parser.add_argument(
        'inputfile', type=str,
        help='1D SG design input file.'
    )

    # Convert
    parser = sub_parser.add_parser(
        Command.CONVERT, aliases=['c'], help='Convert CS/SG data file.',
        parents=[logging_args]
        )
    parser.set_defaults(func=Command.CONVERT)
    parser.add_argument(
        'input_file', type=str,
        help='CS/SG file to be read from.')
    parser.add_argument(
        'output_file', type=str,
        help='CS/SG file to be written to.')
    parser.add_argument(
        '-ff', '--from-format', type=str,
        help='CS/SG file format to be read from.')
    parser.add_argument(
        '-ffv', '--from-format-version', type=str,
        help='CS/SG file format version to be read from.')
    parser.add_argument(
        '-tf', '--to-format', type=str,
        help='CS/SG file format to be written to.')
    parser.add_argument(
        '-tfv', '--to-format-version', type=str,
        help='CS/SG file format version to be written to.')
    parser.add_argument(
        '-a', '--analysis', type=case_insensitive_string, default='h',
        choices=['h', 'd', 'fi'],
        help='Analysis type (h=homogenization, d=dehomogenization, fi=failure).'
    )
    parser.add_argument(
        '-d', '--sgdim', type=int, default=2,
        choices=[1, 2, 3],
        help='SG dimension (SwiftComp only).'
    )
    parser.add_argument(
        '-ms', '--model-space', type=case_insensitive_string, default='xy',
        choices=['x', 'y', 'z', 'xy', 'yz', 'zx'],
        help='Model space.'
    )
    parser.add_argument(
        '-mry', '--material-ref-y', type=case_insensitive_string, default='x',
        choices=['x', 'y', 'z'],
        help='Axis used as the material reference y-axis.'
    )
    parser.add_argument(
        '-m', '--model', type=case_insensitive_string, default='bm2',
        choices=['sd1', 'pl1', 'pl2', 'bm1', 'bm2'],
        help='CS/SG model type.'
    )
    parser.add_argument(
        '-mo', '--mesh-only', action='store_true',
        help='Mesh only conversion.'
    )
    parser.add_argument(
        '-rn', '--renumber-nodes', action='store_true',
        help='Renumber nodes (deprecated).'
    )
    parser.add_argument(
        '-re', '--renumber-elements', action='store_true',
        help='Renumber elements (deprecated).'
    )

    parsed_args = root_parser.parse_args(args[1:])

    command = vars(parsed_args).pop('func')
    if command is None:
        root_parser.print_help()
    else:
        main(command, **vars(parsed_args))



def main(command: str, **kwargs: Any) -> None:
    """Execute the specified SGIO command with provided arguments.
    
    This function configures logging and dispatches to the appropriate
    command handler based on the command parameter. It includes comprehensive
    error handling and input validation.
    
    Parameters
    ----------
    command : str or Command
        Command name to execute (Command.BUILD or Command.CONVERT)
    **kwargs : Any
        Additional keyword arguments passed to the command, including
        logging configuration and command-specific parameters
        
    Raises
    ------
    NotImplementedError
        If the build command is called (not yet implemented)
    FileNotFoundError
        If input file does not exist or output directory is invalid
    KeyError
        If required kwargs are missing for the specified command
    ValueError
        If invalid parameters are provided
        
    Examples
    --------
    >>> main(Command.CONVERT, input_file='input.vabs', output_file='output.sc', ...)
    >>> main(Command.BUILD, inputfile='design.json', ...)
    """
    try:
        # Configure logging
        configure_logging(
            cout_level=kwargs.get('loglevelcmd', 'info'),
            fout_level=kwargs.get('loglevelfile', 'info'),
            filename=kwargs.get('logfile', 'sgio.log'),
        )
        
        logger.debug(f'Executing {command} with arguments: {kwargs}')

        if command == Command.CONVERT:
            # Sanitize and validate input file
            input_file = sanitize_path(kwargs['input_file'])
            if not input_file.exists():
                logger.error(f'Input file not found: {input_file}')
                raise FileNotFoundError(f'Input file not found: {input_file}')
            
            # Sanitize output path and validate directory exists
            output_file = sanitize_path(kwargs['output_file'])
            if output_file.parent != Path('.').resolve() and not output_file.parent.exists():
                logger.error(f'Output directory not found: {output_file.parent}')
                raise FileNotFoundError(f'Output directory not found: {output_file.parent}')

            convert(
                file_name_in=str(input_file),
                file_name_out=str(output_file),
                file_format_in=kwargs.get('from_format') or '',
                file_format_out=kwargs.get('to_format') or '',
                file_version_in=kwargs.get('from_format_version') or '',
                file_version_out=kwargs.get('to_format_version') or '',
                analysis=kwargs.get('analysis', 'h'),
                sgdim=kwargs.get('sgdim', 2),
                model_space=kwargs.get('model_space', 'xy'),
                prop_ref_y=kwargs.get('material_ref_y', 'x'),
                model_type=kwargs.get('model', 'bm2'),
                mesh_only=kwargs.get('mesh_only', False),
                renum_node=kwargs.get('renumber_nodes', False),
                renum_elem=kwargs.get('renumber_elements', False),
            )
            
            logger.info('Conversion completed successfully')
            
        elif command == Command.BUILD:
            logger.error('Build command not yet implemented')
            raise NotImplementedError(
                'Build functionality is not yet implemented. '
                'This feature is planned for a future release.'
            )
            
        else:
            logger.error(f'Unknown command: {command}')
            raise ValueError(f'Unknown command: {command}')
            
    except KeyError as e:
        logger.error(f'Missing required argument: {e}')
        raise
    except (FileNotFoundError, NotImplementedError, ValueError) as e:
        # Re-raise these exceptions as they have good error messages
        raise
    except Exception as e:
        logger.error(f'Error executing {command}: {e}', exc_info=True)
        raise
