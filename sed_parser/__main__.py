"""
Main module

usage:
    python -m parser --site [dse|cse] --page-type=[sharePrice]

sample use-case: 
    curl [URL] -s | python -m parser --site dse --page-type sharePrice
"""

import sed_parser

if __name__ == "__main__":
    sed_parser.run()
