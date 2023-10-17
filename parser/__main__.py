"""
Main module

usage:
    python -m parser --site [dse|cse] --pageType=[sharePrice]

sample use-case: 
    curl [URL] -s | python -m parser --site dse --pageType sharePrice
"""

from parser.input_tool import get_pipe_data


if __name__ == "__main__":
    print(get_pipe_data())
