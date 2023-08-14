import sys
import argparse


def main(*args):
    print(f'args = {args}')

    root_parser = argparse.ArgumentParser(
        prog='sgio',
        description='SG I/O functions',
        formatter_class=argparse.RawTextHelpFormatter,
    )

    sub_parser = root_parser.add_subparsers()

    parser = sub_parser.add_parser(
        'convert', help='Convert SG data file', aliases=['c',]
    )

    parser.add_argument(
        'from', type=str, help='SG file to be read from'
    )
    parser.add_argument(
        '--from-format', '-ff',
        type=str
    )

    parser.add_argument(
        'to', type=str, help='SG file to be written to'
    )

    pargs = root_parser.parse_args(args)

    return


