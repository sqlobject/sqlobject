#!/usr/bin/env python
"""
This script strips bits of examples from a larger script, formats
them as HTML, and writes them out.

You mark snippets of code like:

## Snippet "snippetname"
code...
## End Snippet

Then a file snippets/snippetname.html is created.
"""

import re, os, sys
import warnings

_snippetRE = re.compile(r'^##\s+Snippet\s+"(.*?)"', re.I)
_endSnippetRE = re.compile(r'^##\s+End\s+Snippet', re.I)

def stripSnippets(lines):
    results = {}
    name = None
    for line in lines:
        match = _snippetRE.search(line)
        if match:
            if name is not None:
                warnings.warn('You started snippet %s when snippet %s was not ended'
                              % (match.group(1), name))
            name = match.group(1)
            continue

        match = _endSnippetRE.search(line)
        if match:
            name = None

        if name is None:
            continue

        results.setdefault(name, []).append(line)

    return results

_bodyRE = re.compile(r'<body[^>]*>', re.I)
_endBodyRE = re.compile(r'</body>', re.I)
_preRE = re.compile(r'<pre>\n<tt>\n', re.I)
_endPreRE = re.compile(r'\n</pre>', re.I)

def snipFile(filename):
    f = open(filename)
    d = stripSnippets(f)
    f.close()
    dirname = os.path.join(os.path.dirname(filename), 'snippets')
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    for key, value in d.items():
        fn = os.path.join(dirname, '%s' % key)
        f = open(fn + ".py", 'w')
        f.write(''.join(value))
        f.close()
        os.system('source-highlight -spython -fxhtml -cdefault.css %s > /dev/null 2>&1'
                  % (fn + ".py"))
        f = open(fn + ".py.html")
        c = f.read()
        f.close()
        os.unlink(fn + ".py.html")
        c = c[_bodyRE.search(c).end():]
        c = c[:_endBodyRE.search(c).start()]
        c = _preRE.sub('<pre class="literal-block"><tt>', c)
        c = _endPreRE.sub('</pre>', c)
        f = open(fn + ".html", 'w')
        f.write(c)
        f.close()

def snipAll(dir):
    if dir == sys.argv[0]:
        return
    if dir.endswith('snippets'):
        return
    if os.path.isdir(dir):
        for fn in os.listdir(dir):
            fn = os.path.join(dir, fn)
            snipAll(fn)
    elif dir.endswith('.py'):
        snipFile(dir)

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        args = ['.']
    for arg in args:
        snipAll(arg)
