"""
Input tools module
"""

import sys


def get_pipe_data() -> str:
    """get pipe inout data"""

    if len(sys.argv) == 1:
        return input()
