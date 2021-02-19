#!/usr/bin/env python3
"""
Usage:
  ./line_bisect.py [options] <commands-file> <test>

Options:
  --good=<line>   The line number of a line where the test succeeds.
  --bad=<line>    The line number of a line where the test fails.
"""
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, NamedTuple, Optional

import crayons
from docopt import docopt


class Line(NamedTuple):
    number: int
    command: str

    def run(self) -> bool:
        return run(self.command, description=f'line {line.number}')


@dataclass
class Bisector:
    good_index: Optional[int]
    bad_index: Optional[int]
    lines: List[Line]
    test: str
    iteration: int = 0

    @property
    def target_index(self) -> int:
        if self._has_indices():
            return (self.good_index + self.bad_index) // 2
        return len(self.lines) - 1

    @property
    def target_line(self) -> int:
        return self._line_number(self.target_index)

    @property
    def good_line(self) -> int:
        return self._line_number(self.good_index)

    @property
    def bad_line(self) -> int:
        return self._line_number(self.bad_index)

    @property
    def good_command(self) -> int:
        return self._line_command(self.good_index)

    @property
    def bad_command(self) -> int:
        return self._line_command(self.bad_index)

    @property
    def total_lines(self) -> int:
        return len(self.lines)

    def should_keep_testing(self) -> bool:
        if self._has_indices():
            return abs(self.good_index - self.bad_index) > 1
        return True

    def test_target(self):
        self.iteration += 1

        print(
            crayons.blue(
                f'Running lines 1 to {self.target_line} of {self.total_lines}.'
            )
        )

        for line in self._target_lines():
            if not run(line.command, description=f'line {line.number}'):
                raise Exception(f'Line {line.number} failed.')

        self._update_index(self._run_test())

    def _target_lines(self) -> List[Line]:
        return self.lines[: self.target_index + 1]

    def _update_index(self, success: bool) -> None:
        if success:
            self.good_index = self.target_index
        else:
            self.bad_index = self.target_index

        self.good_index = self.good_index or 0
        self.bad_index = self.bad_index or 0

        print(crayons.red(f'Line {self.bad_line} is bad: {self.bad_command}'))
        print(crayons.green(f'Line {self.good_line} is good: {self.good_command}'))

    def _run_test(self) -> bool:
        success = run(self.test, description='test')

        if success:
            print(
                crayons.green(
                    f'Test passed after line {self.target_line} on iteration {self.iteration}.'
                )
            )
        else:
            print(
                crayons.red(
                    f'Test failed after line {self.target_line} on iteration {self.iteration}.'
                )
            )

        return success

    def _line_number(self, index: int) -> int:
        return self.lines[index].number

    def _line_command(self, index: int) -> str:
        return self.lines[index].command

    def _has_indices(self) -> bool:
        return self.good_index is not None and self.bad_index is not None


def main() -> int:
    arguments = docopt(__doc__)

    lines = []
    with Path(arguments['<commands-file>']).open() as open_file:
        for line_number, command in enumerate(open_file, start=1):
            command = command.strip()
            if _is_command(command):
                lines.append(Line(number=line_number, command=command))

    bisector = _get_bisector(
        arguments['--good'], arguments['--bad'], lines, arguments['<test>']
    )

    while bisector.should_keep_testing():
        bisector.test_target()


    return 0


def run(command: str, description: str) -> bool:
    print(crayons.cyan(f'Running {description}: {command}'))
    return os.system(command) == 0


def _get_bisector(
    good_argument: Optional[str],
    bad_argument: Optional[str],
    lines: List[Line],
    test: str,
) -> Bisector:
    return Bisector(
        good_index=_get_line_index(good_argument, lines),
        bad_index=_get_line_index(bad_argument, lines),
        lines=lines,
        test=test,
    )


def _get_line_index(line_argument: Optional[str], lines: List[Line]) -> int:
    if not line_argument:
        return None
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
