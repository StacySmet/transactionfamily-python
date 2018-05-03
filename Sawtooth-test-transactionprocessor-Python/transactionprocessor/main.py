
import sys
import os
import argparse
import pkg_resources

from sawtooth_sdk.processor.core import TransactionProcessor
from handler import HelloTransactionHandler

sys.path.append('../')

DISTRIBUTION_NAME = 'sawtooth-hellotxp'

def parse_args(args):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '-C', '--connect',
        help='Endpoint for the validator connection')

    parser.add_argument('-v', '--verbose',
                        action='count',
                        default=0,
                        help='Increase output sent to stderr')

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(version),
        help='print version information')

    return parser.parse_args(args)




def main():
    # In docker, the url would be the validator's container name with
    # port 4004
    print("i started")
    print("processor becomes txp on localhost")
    processor = TransactionProcessor(url='tcp://127.0.0.1:4004')
    handler = HelloTransactionHandler()
    print("handler has gotten a value")
    processor.add_handler(handler)
    print("procesor.add_handler(handler)done")
    print("connected with validator")
    processor.start()
    print("i got to the end")

if __name__ == "__main__":
    main()