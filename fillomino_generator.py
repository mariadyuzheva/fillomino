#!/usr/bin/env python3

ERROR_PYTHON_VERSION = 1
ERROR_MODULES_MISSING = 2
ERROR_GENERATING_PUZZLE = 3
ERROR_WRITING_TO_FILE = 4

import sys
import os

if sys.version_info < (3, 6):
    print('Use python >= 3.6', file=sys.stderr)
    sys.exit(ERROR_PYTHON_VERSION)

if sys.platform.startswith('win32'):
    os.system('color')

import argparse

try:
    from fillomino_logic import PuzzleGenerator
except Exception as e:
    print('Game modules not found: "{}"'.format(e), file=sys.stderr)
    sys.exit(ERROR_MODULES_MISSING)


__author__ = 'Dyuzheva Maria'
__email__ = 'mdyuzheva@gmail.com'


def parse_args():
    parser = argparse.ArgumentParser(
        usage='%(prog)s [OPTIONS]',
        description='Fillomino generator',
        epilog='Author: {} <{}>'.format(__author__, __email__))

    parser.add_argument(
        '-s', '--size', type=int,
        metavar='SIZE', help='generate puzzle with size')
    parser.add_argument(
        '-e', '--empty', type=int,
        metavar='PERCENT', help='percent of empty cells')
    parser.add_argument(
        '-u', '--unity', action="store_true", default=False,
        help='allow including blocks with value "1" to empty cells')
    parser.add_argument(
        '-p', '--puzzle', type=str,
        metavar='FILENAME', help='write puzzle to file')
    parser.add_argument(
        '-l', '--solution', type=str,
        metavar='FILENAME', help='write solution to file')
    parser.add_argument(
        '-c', '--color', action="store_true", default=False,
        help='color blocks in 4 colors')
    parser.add_argument(
        '-m', '--maxvalue', type=int,
        metavar='MAXVALUE', help='maximum value of cell')

    return parser.parse_args()


def write_result(file, result, colored):
    if file:
        try:
            with open(file, 'w') as output_file:
                print(result, file=output_file)

        except Exception as e:
            print('Error while writing to file\n{}'.format(e), file=sys.stderr)
            sys.exit(ERROR_WRITING_TO_FILE)

    else:
        if colored:
            result.color_state()
        print(result)


def main():
    args = parse_args()

    if args.size:
        try:
            if args.maxvalue:
                generator = PuzzleGenerator(args.size, args.maxvalue)
            else:
                generator = PuzzleGenerator(args.size)
            generator.generate_filled_field()

            if args.empty:
                generator.generate_field_for_game(bool(args.unity), args.empty)
            else:
                generator.generate_field_for_game(bool(args.unity))

            write_result(args.puzzle, generator.game_field, args.color)
            write_result(args.solution, generator.field_state, args.color)

        except Exception as e:
            print('Error while generating puzzle\n{}'.format(e),
                  file=sys.stderr)
            sys.exit(ERROR_GENERATING_PUZZLE)


if __name__ == '__main__':
    main()
