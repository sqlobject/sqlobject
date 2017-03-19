#! /usr/bin/env python

# Find commit date/time for every commit, list files in the commit
# and set the file's modification time to the date/time of the latest commit.

# Adapted from https://git.wiki.kernel.org/index.php/ExampleScripts#Setting_the_timestamps_of_the_files_to_the_commit_timestamp_of_the_commit_which_last_touched_them  # noqa

import os
import subprocess

separator = '----- GIT LOG SEPARATOR -----'

git_log = subprocess.Popen(['git', 'log', '-m', '--first-parent',
                            '--name-only', '--no-color',
                            '--format=%s%%n%%ct' % separator],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
filenames = set()
# stages: 1 - start of commit, 2 - timestamp, 3 - empty line, 4 - files
stage = 1
while True:
    line = git_log.stdout.readline()
    if not line:  # EOF
        break
    line = line.strip()
    if (stage in (1, 4)) and (line == separator):  # Start of a commit
        stage = 2
    elif stage == 2:
        stage = 3
        time = int(line)
    elif stage == 3:
        if line == separator:  # Null-merge (git merge -s ours), no files
            stage = 2
            continue
        stage = 4
        assert line == '', line
    elif stage == 4:
        filename = line
        if filename not in filenames:
            filenames.add(filename)
            if os.path.exists(filename):
                os.utime(filename, (time, time))
    else:
        raise ValueError("stage: %d, line: %s" % (stage, line))

git_log.wait()
git_log.stdout.close()
