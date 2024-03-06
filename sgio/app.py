import sys
import argparse


def cli(*args):
    print(f'args = {args}')

    root_parser = argparse.ArgumentParser(
        prog='sgio',
        description='SG I/O functions',
        # formatter_class=argparse.RawTextHelpFormatter,
    )

    sub_parser = root_parser.add_subparsers(
        help='sub-command help'
    )

    parser = sub_parser.add_parser(
        'convert', aliases=['c',],
        help='Convert SG data file')
    parser.add_argument(
        'from', type=str,
        help='SG file to be read from')
    parser.add_argument(
        '-ff', '--from-format', type=str,
        help='SG file format to be read from')
    parser.add_argument(
        'to', type=str,
        help='SG file to be written to')
    parser.add_argument(
        '-tf', '--to-format', type=str,
        help='SG file format to be written to')

    pargs = root_parser.parse_args(args[1:])
    print(f'parsed args = {pargs}')

    return



def main():
    ...
