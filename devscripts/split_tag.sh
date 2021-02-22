split_tag() {
   branch=$2
   set -- `echo $1 | sed -e 's/\./ /g' -e 's/a/ alpha /' -e 's/b/ beta /' -e 's/rc/ rc /' -e 's/\([0-9]\)c/\1 rc /' -e 's/post\([0-9]\+\)/ post \1/'`
   major=$1
   minor=$2
   micro=$3
   if [ -n "$4" ]; then
      if [ "$4" = rc ]; then
         state="release candidate"
      else
         state=$4
      fi
      serial=$5
   else
      state=final
      serial=0
   fi

   if [ -z "$branch" ]; then
      branch=$major.$minor
   fi
}
