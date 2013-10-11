import argparse
from publicstatic import conf
from publicstatic import const
from publicstatic import publicstatic
from publicstatic.version import get_version

from pprint import pprint

def parse(args):
    epilog = ("See '%s <command> --help' for more details "
              "on a specific command usage.") % const.PROG
    parser = argparse.ArgumentParser(prog=const.PROG,
                                     epilog=epilog)
    version = '%s v%s' % (const.GENERATOR, get_version())
    parser.add_argument('-v', '--version',
                        action='version',
                        version=version,
                        help='print version number and exit')

    parser.add_argument('-s', '--source',
                        default=None,
                        metavar='DIR',
                        dest='source',
                        help='website source path (default is the cwd)')

    subparsers = parser.add_subparsers(metavar='<command>',
                                       dest='command',
                                       help='')

    # a note related to arguments definition: certainly I remember about DRY
    # principle, but the plain code structure here seem to be more important
    # than don't-repeating thyself

    # init command parser
    help = 'initialize new website'
    subparser = subparsers.add_parser('init', help=help)

    # build command parser
    help = 'generate web content from source'
    subparser = subparsers.add_parser('build', help=help)

    # run command parser
    help = 'run local web server to preview generated website'
    subparser = subparsers.add_parser('run', help=help)
    subparser.add_argument('-p', '--port',
                           default=None,
                           type=int,
                           dest='port',
                           help='port for local HTTP server')
    subparser.add_argument('-b', '--browse',
                           action='store_true',
                           default=False,
                           dest='browse',
                           help='open in default browser')

    # deploy command parser
    help = 'deploy generated website to the remote web server'
    subparser = subparsers.add_parser('deploy', help=help)

    # clean command parser
    help = 'delete all generated content'
    subparser = subparsers.add_parser('clean', help=help)

    # page command parser
    subparser = subparsers.add_parser('page', help='create new page')
    subparser.add_argument('name', help='page name (may include path)')
    subparser.add_argument('-f', '--force',
                           action='store_true',
                           default=False,
                           dest='force',
                           help='overwrite existing file')
    subparser.add_argument('-e', '--edit',
                           action='store_true',
                           default=False,
                           dest='edit',
                           help='open with text editor')

    # post command parser
    subparser = subparsers.add_parser('post', help='create new post')
    subparser.add_argument('name', help='page name (may include path)')
    subparser.add_argument('-f', '--force',
                           action='store_true',
                           default=False,
                           dest='force',
                           help='overwrite existing file')
    subparser.add_argument('-e', '--edit',
                           action='store_true',
                           default=False,
                           dest='edit',
                           help='open with text editor')

    # update command parser
    help = 'update templates to the latest version'
    subparser = subparsers.add_parser('update', help=help)

    # image command parser
    help = 'image management commands group'
    image_subparser = subparsers.add_parser('image', help=help)
    subsubparsers = image_subparser.add_subparsers(metavar='<subcommand>',
                                                   dest='subcommand',
                                                   help='')

    # image.add command parser
    help = 'add new image with optional id'
    subparser = subsubparsers.add_parser('add', help=help)
    subparser.add_argument('filename', help='image file name')
    subparser.add_argument('id',
                           default=None,
                           help='image identifier')

    # image.rm command parser
    subparser = subsubparsers.add_parser('rm', help='remove image')
    subparser.add_argument('id',
                           default=None,
                           help='image identifier')

    # image.list command parser
    subparser = subsubparsers.add_parser('ls', help='list images')
    default = 10
    help = 'output the last N lines, instead of the last %d' % default
    subparser.add_argument('-n', '--lines',
                           default=default,
                           type=int,
                           dest='number',
                           metavar='N',
                           help=help)

    result = vars(parser.parse_args(args))
    command = result.get('command', None)
    subcommand = result.get('subcommand', None)

    if command is None:
        parser.print_help()
    elif command == 'image' and subcommand is None:
        image_subparser.print_help()

    return result