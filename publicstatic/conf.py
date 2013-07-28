# coding: utf-8

"""Configuration-related fuctionality and defaults"""

import codecs
from datetime import datetime
import os
import yaml
from publicstatic import constants
from publicstatic.version import get_version

_params = {}  # Configuration parameters
_path = ''  # Configuration file absolute path


def init(conf_path, use_defaults=False):
    """Initializes configuration"""
    global _path
    _path = os.path.abspath(os.path.join(conf_path or '.', constants.CONF_NAME))
    params = dict(zip(map(lambda p: p['name'], constants.DEFAULTS),
                      map(lambda p: p['value'], constants.DEFAULTS)))

    if not use_defaults:  # Reads configuration file and override defaults
        try:
            with codecs.open(_path, mode='r', encoding='utf8') as f:
                loaded = yaml.load(f.read())
        except (IOError, OSError) as e:
            raise Exception('configuration file not found') from e

        loaded = dict((item, loaded[item]) for item in loaded)
        params.update(loaded)

    global _params
    _params = _purify(params)


def get(param):
    """Returns a single configuration parameter"""
    try:
        return _params[param]
    except KeyError:
        raise Exception('Unknown configuration parameter')
    except TypeError:
        raise Exception('Configuration was not initialized')


def get_path():
    _check(_path)
    return _path


def _dump_option(option):
    name, value, desc = option['name'], option['value'], option['desc']
    srl = yaml.dump({name: value}, width=80, indent=4, default_flow_style=False)
    return ''.join([("# %s\n" % desc) if desc else '', srl])


def write_defaults():
    """Write default configuration to specified file"""
    _check(_path)
    text = '\n'.join([_dump_option(option) for option in constants.DEFAULTS])
    with codecs.open(_path, mode='w', encoding='utf8') as f:
        f.write(text)


def _check(value):
    if not value:
        raise Exception('Configuration was not initialized')


def _purify(params):
    """Preprocess configuration parameters"""
    params['pages_path'] = _expand(params['pages_path'])
    params['posts_path'] = _expand(params['posts_path'])
    params['assets_path'] = _expand(params['assets_path'])
    params['build_path'] = _expand(params['build_path'])
    params['tpl_path'] = _expand(params['tpl_path'])
    params['prototypes_path'] = _expand(params['prototypes_path'])

    params['root_url'] = _trslash(params['root_url'].strip())
    params['rel_root_url'] = _trslash(params['rel_root_url'].strip())
    params['source_url'] = _trslash(params['source_url'].strip())

    params['browser_delay'] = float(params['browser_delay'])
    params['port'] = int(params['port'])

    params['log_file'] = params['log_file'].strip()
    params['log_max_size'] = int(params['log_max_size'])
    params['log_backup_cnt'] = int(params['log_backup_cnt'])

    if isinstance(params['time_format'], str):
        params['time_format'] = [params['time_format']]

    # If there is no {suffix}, include it before extension
    post_loc = params['post_location']
    if '{suffix}' not in post_loc:
        name, ext = os.path.splitext(post_loc)
        params['post_location'] = ''.join([name, '{suffix}', ext])

    menu = params['menu']
    for item in menu:
        item['href'] = item['href'].strip() if 'href' in item else ''
        item['title'] = item['title'].strip() if 'title' in item else ''
    return params


def _expand(rel_path):
    """Expands relative path using configuration file location as base
    directory. Absolute pathes will be returned as is."""
    if not os.path.isabs(rel_path):
        base = os.path.dirname(os.path.abspath(_path))
        rel_path = os.path.join(base, rel_path)
    return rel_path


def  _trslash(url):
    """Guarantees the URL have a single trailing slash"""
    return url.rstrip('/') + '/'
