# coding: utf-8

"""public-static - static website builder."""

from datetime import datetime
from multiprocessing import Process
import os
import re
import shutil
import sys
from argh import ArghParser, arg
from publicstatic import conf
from publicstatic import const
from publicstatic import creators
from publicstatic import builders
from publicstatic import logger
from publicstatic import helpers
from publicstatic.cache import Cache
from publicstatic.version import get_version

# Common command line arguments

source_arg = arg('-s', '--source',
                 default=None,
                 metavar='DIR',
                 help='website source path (default is the current directory)')

force_arg = arg('-f', '--force',
                default=False,
                help='overwrite existing file')

edit_arg = arg('-e', '--edit',
               default=False,
               help='open with preconfigured editor')

# Commands

@source_arg
def init(args):
    """create new website"""
    conf.generate(args.source)
    try:
        helpers.spawn_site(conf.site_dir())
        logger.info('website created successfully, have fun!')
    except Exception as ex:
        logger.error('initialization failed: ' + str(ex))
        print(str(ex))


@source_arg
def build(args):
    """generate web content from source"""
    conf.load(args.source)
    cache = Cache()
    steps = [
            builders.css,
            builders.js,
            builders.less,
            builders.robots,
            builders.humans,
            builders.static,
            builders.pages,
            builders.posts,
            # builders.archive,
            # builders.tags,
            # builders.rss,
            # builders.atom,
            # builders.sitemap,
        ]

    for builder in steps:
        try:
            builder(cache)
        except Exception as ex:
            # logger.error(str(ex))
            raise

    # helpers.drop_build(conf.get('build_path'))
    # helpers.makedirs(conf.get('build_path'))

    # logger.info("building path: '%s'" % conf.get('build_path'))
    # logger.info('processing assets...')
    # builders.process_dir(conf.get('assets_path'))

    # logger.info('processing blog posts...')
    # builders.process_blog(conf.get('posts_path'))

    # logger.info('processing pages...')
    # builders.process_dir(conf.get('pages_path'))
    # logger.info('done')


@source_arg
@arg('-p', '--port', default=None, help='port for local HTTP server')
@arg('-b', '--browse', default=False, help='open in default browser')
def run(args):
    """run local web server to preview generated website"""
    conf.load(args.source)
    helpers.check_build(conf.get('build_path'))
    original_cwd = os.getcwd()
    port = helpers.str2int(args.port, conf.get('port'))
    logger.info("running HTTP server on port %d..." % port)

    from http.server import SimpleHTTPRequestHandler
    from socketserver import TCPServer
    handler = SimpleHTTPRequestHandler
    httpd = TCPServer(('', port), handler)

    try:
        if args.browse:
            url = "http://localhost:%s/" % port
            logger.info("opening browser in %g seconds" % const.BROWSER_DELAY)
            p = Process(target=helpers.browse, args=(url, const.BROWSER_DELAY))
            p.start()

        logger.info('use Ctrl-Break to stop webserver')
        os.chdir(conf.get('build_path'))
        httpd.serve_forever()

    except KeyboardInterrupt:
        logger.info('server was stopped by user')
    finally:
        os.chdir(original_cwd)


@source_arg
def deploy(args):
    """deploy generated website to the remote web server"""
    conf.load(args.source)
    helpers.check_build(conf.get('build_path'))

    if not conf.get('deploy_cmd'):
        raise Exception('deploy command is not defined')

    logger.info('deploying website...')
    cmd = conf.get('deploy_cmd').format(build_path=conf.get('build_path'))

    from subprocess import call
    call(cmd)

    logger.info('done')


@source_arg
def clean(args):
    """delete all generated content"""
    conf.load(args.source)
    logger.info('cleaning output...')
    helpers.drop_build(conf.get('build_path'))
    logger.info('done')


@arg('name', help='page name (may include path)')
@source_arg
@force_arg
@edit_arg
def page(args):
    """create new page"""
    conf.load(args.source)
    text = helpers.prototype('default-page')
    try:
        path = creators.newpage(args.name, text, args.force)
    except creators.PageExistsException:
        logger.error('page already exists, use -f to overwrite')
        return

    logger.info('page created: ' + path)
    if args.edit:
        helpers.execute(conf.get('editor_cmd'), path)


@arg('name', help='post name and optional feed name')
@source_arg
@force_arg
@edit_arg
def post(args):
    """create new post"""
    conf.load(args.source)
    text = helpers.prototype('default-post')
    path = creators.newpost(args.name, text, args.force)
    logger.info('post created: ' + path)
    if args.edit:
        helpers.execute(conf.get('editor_cmd'), path)


@source_arg
def update(args):
    """update templates and prototypes to the latest version"""
    conf.load(args.source)
    site_dir = conf.site_dir()

    def replace(subject, dir_name):
        tmp = dir_name + '_'
        if os.path.isdir(dir_name):
            os.rename(dir_name, tmp)
        helpers.copydir(helpers.gen_dir(subject), os.path.join(site_dir, subject))
        if os.path.exists(tmp):
            shutil.rmtree(tmp)

    logger.info('updating templates')
    replace(const.TEMPLATES_DIR, conf.get('tpl_path'))
    logger.info('updating prototypes')
    replace(const.PROTO_DIR, conf.get('prototypes_path'))
    logger.info('done')


def version(args):
    """show version"""
    return get_version()


def main():
    try:
        p = ArghParser(prog='pub')
        p.add_commands([init, build, run, deploy, clean, page, post, update, version])
        p.dispatch()
    except Exception:
        # logger.crash()
        raise
