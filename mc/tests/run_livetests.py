#!/usr/bin/env python
"""
Find and run the unit tests
"""

import unittest
import sys
sys.path.append('../../')

if __name__ == '__main__':
    suite = unittest.TestLoader().discover('livetests')
    results = unittest.TextTestRunner(verbosity=3).run(suite)
    if results.errors or results.failures:
        sys.exit(1)