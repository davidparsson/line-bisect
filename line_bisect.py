#!/usr/bin/env python3
"""
Usage:
  ./line_bisect.py [options] <commands-file> <test> [--good=<line>] [--bad=<line>]

Options:
  --good=<line>   The line number of a line where the test succeeds. [default: 1]
  --bad=<line>    The line number of a line where the test fails. [default: -1]
"""
import os
import sys
from pathlib import Path
from typing import List
from typing import NamedTuple

import crayons
from docopt import docopt


class Line(NamedTuple):
    number: int
    command: str


def main() -> int:
    arguments = docopt(__doc__)

    lines = []
    with Path(arguments['<commands-file>']).open() as open_file:
        for line_number, command in enumerate(open_file, start=1):
            command = command.strip()
            if _is_command(command):
                lines.append(Line(number=line_number, command=command))

    total_lines = len(lines)

    def _line_number(index: int) -> int:
        return lines[index].number

    test = arguments['<test>']
    good_index = _get_line_index(arguments['--good'], lines)
    bad_index = _get_line_index(arguments['--bad'], lines)
    iteration = 0

    while abs(good_index - bad_index) > 1:
        iteration += 1
        target_index = (good_index + bad_index) // 2
        target_line = _line_number(target_index)

        print(crayons.blue(f'Running lines 1 to {target_line} of {total_lines}.'))
        success = run_lines(lines, target_index, test)
        if success:
            print(crayons.green(f'Test passed after line {target_line} on iteration {iteration}.'))
            good_index = target_index
        else:
            print(crayons.red(f'Test failed after line {target_line} on iteration {iteration}.'))
            bad_index = target_index

        print(crayons.red(
            f'Line {_line_number(bad_index)} is bad: {lines[bad_index].command}'
        ))
        print(crayons.green(
            f'Line {_line_number(good_index)} is good: {lines[good_index].command}'
        ))
    return 0


def run_lines(lines: List[Line], run_until_index: int, test: str) -> bool:
    for line in lines[:run_until_index + 1]:
        if not run(line.command, description=f'line {line.number}'):
            raise Exception(f'Line {line.number} failed.')
    return run(test, description='test')


def run(command: str, description: str) -> bool:
    print(crayons.cyan(f'Running {description}: {command}'))
    return os.system(command) == 0


def _get_line_index(line_argument: str, lines: List[Line]) -> int:
    line_number_argument = int(line_argument)
    if line_number_argument == -1:
        return len(lines) - 1
    for line_index, line in enumerate(lines):
        if line.number >= line_number_argument:
            return line_index
    return len(lines) - 1


def _is_command(command: str) -> bool:
    return bool(command) and not command.startswith('#')


if __name__ == '__main__':
    sys.exit(main())
