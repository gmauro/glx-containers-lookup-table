import argparse
import os

from comoda import a_logger, LOG_LEVELS, ensure_dir
from src import *
from importlib import import_module

SUBMOD_NAMES = [
    "src.cli.info",
    "src.cli.build",
]
SUBMODULES = [import_module(n) for n in SUBMOD_NAMES]


class App(object):
    def __init__(self):
        self.supported_submodules = []
        for m in SUBMODULES:
            m.do_register(self.supported_submodules)

    def make_parser(self):
        parser = argparse.ArgumentParser(prog=__appname__,
                                         description='Galaxy containers lookup table builder',
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('--logfile', type=str, metavar='PATH',
                            help='log file', default=log_file)
        parser.add_argument('--loglevel', type=str, help='logger level.',
                            choices=LOG_LEVELS, default='INFO')
        parser.add_argument('-v', '--version', action='version',
                            version='%(prog)s {}'.format(__version__))

        subparsers = parser.add_subparsers(dest='subparser_name',
                                           title='subcommands',
                                           description='valid subcommands',
                                           help='sub-command description')

        for k, h, addarg, impl in self.supported_submodules:
            subparser = subparsers.add_parser(k, help=h)
            addarg(subparser)

        subparser.set_defaults(func=impl)

        return parser


def main():
    app = App()
    parser = app.make_parser()
    args = parser.parse_args()
    ensure_dir(os.path.dirname(args.logfile))
    logger = a_logger('Main', level=args.loglevel, filename=args.logfile)
    logger.info('{} started'.format(__appname__.capitalize()))

    args.func(logger, args) if hasattr(args, 'func') else parser.print_help()


if __name__ == '__main__':
    main()
