# added to work with documentation generation
try:
    import bluecat
except ImportError:
    import os
    import sys
    sys.path.insert(0, os.path.abspath('..'))
