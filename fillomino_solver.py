#!/usr/bin/env python3

ERROR_PYTHON_VERSION = 1
ERROR_MODULES_MISSING = 2
ERROR_SOLVING_PUZZLE = 3
ERROR_READING_FROM_FILE = 4
ERROR_WRITING_TO_FILE = 5

import sys
import os

if sys.version_info < (3, 6):
    print('Use python >= 3.6', file=sys.stderr)
    sys.exit(ERROR_PYTHON_VERSION)

if sys.platform.startswith('win32'):
    os.system('color')

import argparse

try:
    from fillomino_logic import PuzzleSolver
except Exception as e:
    print('Game modules not found: "{}"'.format(e), file=sys.stderr)
    sys.exit(ERROR_MODULES_MISSING)


__author__ = 'Dyuzheva Maria'
__email__ = 'mdyuzheva@gmail.com'


def parse_args():
    parser = argparse.ArgumentParser(
        usage='%(prog)s [OPTIONS]',
        description='Fillomino solver',
        epilog='Author: {} <{}>'.format(__author__, __email__))

    parser.add_argument(
        '-s', '--solve', type=str,
        metavar='FILENAME', help='solve puzzle from file')
    parser.add_argument(
        '-u', '--unity', action="store_true", default=False,
        help='allow including blocks with value "1" to empty cells')
    parser.add_argument(
        '-w', '--write', type=str,
        metavar='FILENAME', help='write solution to file')
    parser.add_argument(
        '-c', '--color', action="store_true", default=False,
        help='color blocks in 4 colors')
    parser.add_argument(
        '-r', '--strict', action="store_true", default=False,
        help='every block (except maybe "1") '
             'has at least one value on the field')

    return parser.parse_args()


def write_solution(puzzle, unity, filename, colored, strict):
    try:
        solver = PuzzleSolver(puzzle, bool(unity), bool(strict))
        solver.solve()

        if filename:
            try:
                with open(filename, 'w') as output_file:
                    print(solver.field_state, file=output_file)

            except Exception as e:
                print('Error while writing to file\n{}'.format(e),
                      file=sys.stderr)
                sys.exit(ERROR_WRITING_TO_FILE)

        else:
            if colored:
                solver.field_state.color_state()
            print(solver.field_state)

    except Exception as e:
        print('Error while solving puzzle\n{}'.format(e),
              file=sys.stderr)
        sys.exit(ERROR_SOLVING_PUZZLE)


def main():
    args = parse_args()

    if not sys.stdin.isatty():
        try:
            puzzle = sys.stdin.read()

        except Exception as e:
            print('Error while reading from file\n{}'.format(e),
                  file=sys.stderr)
            sys.exit(ERROR_READING_FROM_FILE)

        write_solution(puzzle, args.unity, args.write, args.color, args.strict)

    if args.solve:
        try:
            with open(args.solve, 'r') as input_file:
                puzzle = input_file.read()

        except Exception as e:
            print('Error while reading from file\n{}'.format(e),
                  file=sys.stderr)
            sys.exit(ERROR_READING_FROM_FILE)

        write_solution(puzzle, args.unity, args.write, args.color, args.strict)


if __name__ == '__main__':
    main()
