# Line Bisect
Finds issues in sequences of commands, by executing parts of them

## Example

Create a file that contains sequences of commands. This is the contents of `example.txt`:

```
echo foo > output.log
echo FOOBAR >> output.log
echo foo >> output.log; echo foo >> output.log
```

Example execution:
```
$ ./line_bisect.py example.txt 'grep FOOBAR output.log'
Running lines 1 to 3 of 3.
Running line 1: echo foo > output.log
Running line 2: echo FOOBAR >> output.log
Running line 3: echo foo >> output.log; echo foo >> output.log
Running test: grep FOOBAR output.log
FOOBAR
Test passed after line 3 on iteration 1.
Line 1 is bad: echo foo > output.log
Line 3 is good: echo foo >> output.log; echo foo >> output.log
Running lines 1 to 2 of 3.
Running line 1: echo foo > output.log
Running line 2: echo FOOBAR >> output.log
Running test: grep FOOBAR output.log
FOOBAR
Test passed after line 2 on iteration 2.
Line 1 is bad: echo foo > output.log
Line 2 is good: echo FOOBAR >> output.log
```

## Command-line options

```
$ ./line_bisect.py --help
Usage:
  ./line_bisect.py [options] <commands-file> <test>

Options:
  --good=<line>   The line number of a line where the test succeeds.
  --bad=<line>    The line number of a line where the test
  ```
