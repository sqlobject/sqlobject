#! /bin/sh

. `dirname $0`/split.sh &&
split_tag 21.12.42c4

test_eq() {
   if [ "$1" != "$2" ]; then
      echo "$1" != "$2" >&2
   fi
}

test_eq "$branch" 21.12
test_eq "$major" 21
test_eq "$minor" 12
test_eq "$micro" 42
test_eq "$state" "release candidate"
test_eq "$serial" 4
