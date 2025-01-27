# import sys
import argparse

import sgio._global as GLOBAL
import logging
logger = logging.getLogger(GLOBAL.LOGGER_NAME)

from .iofunc import convert


def cli(*args):
    # print(f'args = {args}')

    root_parser = argparse.ArgumentParser(
        prog='sgio',
        description='CS/SG I/O functions',
        # formatter_class=argparse.RawTextHelpFormatter,
    )
    root_parser.set_defaults(func=None)

    sub_parser = root_parser.add_subparsers(
        help='sub-command help'
    )

    # Build
    parser = sub_parser.add_parser(
        'build', aliases=['b',],
        help='Build 1D SG')
    parser.set_defaults(func='build')
    parser.add_argument(
        'inputfile', type=str,
        help='1D SG design input file'
    )

    # Convert
    parser = sub_parser.add_parser(
        'convert', aliases=['c',],
        help='Convert CS/SG data file')
    parser.set_defaults(func='convert')
    parser.add_argument(
        'from', type=str,
        help='CS/SG file to be read from')
    parser.add_argument(
        '-ff', '--from-format', type=str,
        help='CS/SG file format to be read from')
    parser.add_argument(
        'to', type=str,
        help='CS/SG file to be written to')
    parser.add_argument(
        '-tf', '--to-format', type=str,
        help='CS/SG file format to be written to')
    parser.add_argument(
        '-d', '--sgdim', type=int, default=2,
        help='SG dimension (SwiftComp only)'
    )
    parser.add_argument(
        '-m', '--model', type=str, default='BM2',
        help='CS/SG model'
    )
    parser.add_argument(
        '-mo', '--mesh-only', action='store_true',
        help='Mesh only conversion'
    )

    pargs = root_parser.parse_args(args[1:])
    # print(f'parsed args = {pargs}')

    func = vars(pargs).pop('func')
    if func is None:
        root_parser.print_help()
    else:
        main(func, **vars(pargs))

    return



def main(func, **kwargs):
    """
    """

    if func == 'convert':

        convert(
            file_name_in=kwargs['from'],
            file_name_out=kwargs['to'],
            file_format_in=kwargs['from_format'],
            file_format_out=kwargs['to_format'],
            sgdim=kwargs['sgdim'],
            model_type=kwargs['model'],
            mesh_only=kwargs['mesh_only'],
        )
