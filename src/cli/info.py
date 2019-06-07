from src import *


help_doc = """
Show Galaxy containers lookup table details
"""


def make_parser(parser):
    pass


def implementation(logger, args):
    print("App: {} {}\n".format(__appname__, __version__))

    src_path = {
                   'log file': log_file
                   }
    print("Paths: ")
    for k, v in src_path.items():
        print("  {}: {}".format(k, v))
    print("\n")


def do_register(registration_list):
    registration_list.append(('info', help_doc, make_parser, implementation))
