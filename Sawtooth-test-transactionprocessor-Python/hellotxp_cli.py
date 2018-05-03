from __future__ import print_function

import argparse
import getpass
import logging
import os
import traceback
import sys
import pkg_resources

from colorlog import ColoredFormatter

from hellotxp_client import hellotxpClient
from hellotxp_exceptions import HellotxpException

DISTRIBUTION_NAME = 'sawtooth-hellotxp'
DEFAULT_URL = 'http://127.0.0.1:8008'

def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s"
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
             'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })
    clog.setFormatter(formatter)

    if verbose_level == 0:
        clog.setLevel(logging.WARN)
    elif verbose_level ==1:
        clog.setLevel(logging.INFO)
    else:
        clog.setLevel(logging.DEBUG)

    return clog

def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))

def add_create_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'create',
        help='Creates a new harvestbatch',
        description='Sends a transaction to create a harvestbatch '
        'identifier <name>. This transaction will fail if the specified '
        'batch already exists.',
        parents=[parent_parser])

    parser.add_argument(
        'name',
        type=str,
        help='unique identifier for the new batch'
    )

    parser.add_argument(
        '--url',
        type=str,
        help="identify name of user's private key file"
    )

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file"
    )

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication of REST API us using Basic Auth'
    )

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
             'is using Basic Auth')

    parser.add_argument(
        '--disable-client-validation',
        action='store_true',
        default=False,
        help='disable client validation')

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for game to commit')

def add_delete_parser(subparsers, parent_parser):
    parser = subparsers.add_parser('delete', parents=[parent_parser])

    parser.add_argument(
        'name',
        type=str,
        help='name of the batch to be deleted')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for delete transaction to commit')
def add_listitem_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
    'listitem',
    help='display information from a specific batch',
    description='show all information in state from a specific batch '
    'showing name etc.',
     parents=[parent_parser],

    )
    parser.add_argument(
        'name',
        type=str,
        help='name of the batch to be shown')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
             'is using Basic Auth')
    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
             'is using Basic Auth')


def add_list_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'list',
        help='display information from all harvest batches',
        description='show all information in state from all harvest batches '
                    'showing name etc.',
        parents=[parent_parser],

    )

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
             'is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
             'is using Basic Auth')


def create_parent_parser(prog_name):
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    parent_parser.add_argument(
        '-v', '--verbose',
        action='count',
        help='enable more verbose output')

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(version),
        help='display version information')

    return parent_parser


def create_parser(prog_name):
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        description='provides subcommands for creating harvestbatches ',
        parents=[parent_parser])

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    subparsers.required = True

    add_create_parser(subparsers, parent_parser)
    add_list_parser(subparsers, parent_parser)
    add_listitem_parser(subparsers, parent_parser)
    #add_show_parser(subparsers, parent_parser)
    #add_take_parser(subparsers, parent_parser)
    add_delete_parser(subparsers, parent_parser)

    return parser


def do_create(args):
    name = args.name

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    auth_user, auth_password = _get_auth_info(args)

    client = hellotxpClient(base_url=url, keyfile=keyfile)

    if args.wait and args.wait > 0:
        response = client.create(
            name, wait=args.wait,
            auth_user=auth_user,
            auth_password=auth_password)
    else:
        response = client.create(
            name, auth_user=auth_user,
            auth_password=auth_password)

    print("Response: {}".format(response))

def do_delete(args):
    name = args.name

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    auth_user, auth_password = _get_auth_info(args)

    client = hellotxpClient(base_url=url, keyfile=keyfile)

    if args.wait and args.wait > 0:
        response = client.delete(
            name, wait=args.wait,
            auth_user=auth_user,
            auth_password=auth_password)
    else:
        response = client.delete(
            name, auth_user=auth_user,
            auth_password=auth_password)

    print("Response: {}".format(response))

def do_list(args):
    auth_user, auth_password = _get_auth_info(args)

    url = _get_url(args)
    client = hellotxpClient(base_url=url,keyfile=None)

    harvest_list = [
        batch.split(',')
        for batches in client.list(auth_user=auth_user,
                                   auth_password=auth_password)
        for batch in batches.decode().split('|')

    ]

    if harvest_list is not None:
        for batch_data in harvest_list:

            name,batchnr = batch_data

            print(name + ',' + batchnr)
    else:
        raise HellotxpException("No harvest batches to list")

def do_listitem(args):
    auth_user, auth_password = _get_auth_info(args)
    name=args.name
    url = _get_url(args)
    client = hellotxpClient(base_url=url,keyfile=None)
    data = client.show(name, auth_user=auth_user, auth_password=auth_password)
    if data is not None:
        batch_str, batchnr_str = {
            name: (name, batchnr)
            for name, batchnr in [
                batch.split(',')
                for batch in data.decode().split('|')
            ]
        }[name]
        batch = list(batch_str.replace("-", " "))
        print("name:    : {}".format(name))
        print("batch_nr:: {}".format(batchnr_str))
    else:
        raise HellotxpException("Batch not found: {}".format(name))


def _get_url(args):
    return DEFAULT_URL if args.url is None else args.url


def _get_keyfile(args):
   # username = getpass.getuser() if args.username is None else args.username
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, 'ubuntu')

def _get_auth_info(args):
    auth_user = args.auth_user
    auth_password = args.auth_password
    if auth_user is not None and auth_password is None:
        auth_password = getpass.getpass(prompt="Auth Password: ")

    return auth_user, auth_password

def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    if args.verbose is None:
        verbose_level = 0
    else:
        verbose_level = args.verbose

    setup_loggers(verbose_level=verbose_level)

    if args.command == 'create':
        do_create(args)
    elif args.command == 'list':
        do_list(args)
    elif args.command == 'listitem':
        do_listitem(args)
   # elif args.command == 'show':
   #     do_show(args)
   # elif args.command == 'take':
   #     do_take(args)
    elif args.command == 'delete':
        do_delete(args)
    else:
        raise HellotxpException("invalid command: {}".format(args.command))


def main_wrapper():
    try:
        main()
    except HellotxpException as err:
        print("Error: {}".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main_wrapper()