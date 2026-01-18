#!/usr/bin/env python3
"""
A Working Quine - actually prints its own source code.

Run this and pipe to a file, then diff with the original!
    python working_quine.py > copy.py
    diff working_quine.py copy.py

The output should be identical to the source.
"""

s = '''#!/usr/bin/env python3
"""
A Working Quine - actually prints its own source code.

Run this and pipe to a file, then diff with the original!
    python working_quine.py > copy.py
    diff working_quine.py copy.py

The output should be identical to the source.
"""

s = {s!r}

print(s.format(s=s))
'''

print(s.format(s=s))
