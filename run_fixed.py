#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixed launcher for Python version with proper encoding
"""

import sys
import os

# Force UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Now import and run
sys.path.insert(0, os.path.dirname(__file__))

from main import main

if __name__ == '__main__':
    main()
