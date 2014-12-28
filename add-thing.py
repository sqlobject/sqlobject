#!/usr/bin/python
def process_filename(filename):
    lines = open(filename).readlines()
    return process_string(lines)

def process_string(lines):
    # Find first line, rofl
    output_index = None

    for i, line in enumerate(lines):
        if output_index is not None:
            return output_index

        if line.startswith("#"):
             pass
        elif line.startswith("'''"):
             output_index = i
        elif line.startswith('"""'):
             output_index = i
        elif line.startswith('import '):
             output_index = i
        elif line.startswith('from '):
             output_index = i

def fix_filename(filename):
    # OK let's rock it.
    lines = open(filename).readlines()
    # Number
    number = process_filename(filename)
    lines[number:number+1] = ['from __future__ import absolute_import\n\n', lines[number]]

    # Write it
    s = ''.join(lines)
    open(filename, 'w').write(s)

def main():
    import sys
    fix_filename(sys.argv[1])

if __name__ == '__main__':
    main()
