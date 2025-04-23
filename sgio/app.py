# import sys
import argparse
import logging

from sgio import __version__
from sgio._global import logger, configure_logging
# import sgio._global as GLOBAL
from sgio.iofunc import convert

# logger = logging.getLogger(__name__)


def case_insensitive_string(value):
    """Convert string to lowercase for case-insensitive comparison."""
    return value.lower()


def cli(*args):
    # print(f'args = {args}')

    root_parser = argparse.ArgumentParser(
        prog='sgio',
        description='I/O library for VABS (cross-section) and SwiftComp (structural gene)',
        # formatter_class=argparse.RawTextHelpFormatter,
    )
    root_parser.set_defaults(func=None)
    root_parser.add_argument(
        '-v', '--version', action='version', version=__version__,
        help='Show version number and exit'
    )

    # Add logging arguments to each subparser
    logging_args = argparse.ArgumentParser(add_help=False)
    logging_args.add_argument(
        '--loglevelcmd', help='Command line logging level',
        default='info', choices=['debug', 'info', 'warning', 'error', 'critical'])
    logging_args.add_argument(
        '--loglevelfile', help='File logging level',
        default='info', choices=['debug', 'info', 'warning', 'error', 'critical'])
    logging_args.add_argument(
        '--logfile', help='Logging file name',
        default='log.txt')

    sub_parser = root_parser.add_subparsers(
        help='sub-command help'
    )

    # Build
    parser = sub_parser.add_parser(
        'build', aliases=['b',], help='Build 1D SG',
        parents=[logging_args]
        )
    parser.set_defaults(func='build')
    parser.add_argument(
        'inputfile', type=str,
        help='1D SG design input file'
    )

    # Convert
    parser = sub_parser.add_parser(
        'convert', aliases=['c',], help='Convert CS/SG data file',
        parents=[logging_args]
        )
    parser.set_defaults(func='convert')
    parser.add_argument(
        'from', type=str,
        help='CS/SG file to be read from')
    parser.add_argument(
        'to', type=str,
        help='CS/SG file to be written to')
    parser.add_argument(
        '-ff', '--from-format', type=str,
        help='CS/SG file format to be read from')
    parser.add_argument(
        '-ffv', '--from-format-version', type=str,
        help='CS/SG file format version to be read from')
    parser.add_argument(
        '-tf', '--to-format', type=str,
        help='CS/SG file format to be written to')
    parser.add_argument(
        '-tfv', '--to-format-version', type=str,
        help='CS/SG file format version to be written to')
    parser.add_argument(
        '-d', '--sgdim', type=int, default=2,
        choices=[1, 2, 3],
        help='SG dimension (SwiftComp only)'
    )
    parser.add_argument(
        '-ms', '--model-space', type=case_insensitive_string, default='xy',
        choices=['x', 'y', 'z', 'xy', 'yz', 'zx'],
        help='Model space'
    )
    parser.add_argument(
        '-mry', '--material-ref-y', type=case_insensitive_string, default='x',
        choices=['x', 'y', 'z'],
        help='Axis used as the material reference y-axis'
    )
    parser.add_argument(
        '-m', '--model', type=case_insensitive_string, default='bm2',
        choices=['sd1', 'pl1', 'pl2', 'bm1', 'bm2'],
        help='CS/SG model'
    )
    parser.add_argument(
        '-mo', '--mesh-only', action='store_true',
        help='Mesh only conversion'
    )
    parser.add_argument(
        '-re', '--renumber-elements', action='store_true',
        help='Renumber elements'
    )

    pargs = root_parser.parse_args(args[1:])
    # print(f'parsed args = {pargs}')

    func = vars(pargs).pop('func')
    if func is None:
        root_parser.print_help()
    else:
        main(func, **vars(pargs))

    return



def main(
    func, **kwargs):
    """
    """
    print(locals())

    configure_logging(
        cout_level=kwargs['loglevelcmd'],
        fout_level=kwargs['loglevelfile'],
        filename=kwargs['logfile'],
    )

    if func == 'convert':

        convert(
            file_name_in=kwargs['from'],
            file_name_out=kwargs['to'],
            file_format_in=kwargs['from_format'],
            file_format_out=kwargs['to_format'],
            file_version_in=kwargs['from_format_version'],
            file_version_out=kwargs['to_format_version'],
            sgdim=kwargs['sgdim'],
            model_space=kwargs['model_space'],
            prop_ref_y=kwargs['material_ref_y'],
            model_type=kwargs['model'],
            mesh_only=kwargs['mesh_only'],
            renum_elem=kwargs['renumber_elements'],
        )
