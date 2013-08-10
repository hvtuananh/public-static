# coding: utf-8

"""Jinja2 helpers."""

import jinja2
import codecs
from urllib.parse import urlparse, urljoin
from publicstatic import conf

_env = None


def env():
    global _env

    if _env is None:
        loader = jinja2.FileSystemLoader(searchpath=conf.get('tpl_path'))
        _env = jinja2.Environment(loader=loader)
        _env.filters['datetime'] = filter_datetime
        _env.filters['date'] = filter_date
        _env.filters['isodatetime'] = filter_isodatetime
        _env.filters['trimurl'] = filter_trimurl

    return _env


def filter_datetime(value):
    return value.strftime(conf.get('page_datetime_format'))


def filter_date(value):
    return value.strftime(conf.get('page_date_format'))


def filter_isodatetime(value):
    return value.isoformat()


def filter_trimurl(value):
    """Trims addressing scheme (protocol) from the specified url."""
    url = urlparse(value)
    return url.netloc + url.path.rstrip('/')


def template(name=None, path=None, format='html'):
    """Gets template file contents.

    Arguments:
        name -- template name (file base name w/o extension).
        path -- template file full path, an alternative way to specify
            the template.
        format -- template format (file extension), must be specified
            if the template is defined by name."""
    if name:
        return env().get_template("%s.%s" % (name, format))
    elif path:
        with codecs.open(path, mode='r', encoding='utf-8') as f:
            return env().from_string(f.read())
    else:
        raise Exception('either template name or path should be specified')


def render(data=None, name=None, path=None, format='html', dest=None):
    """Render data using a specified template to a file."""
    if not path:
        name = name or data['page']['template']
    tpl = template(name=name, path=path, format=format)
    result = tpl.render(data)

    if dest:
        with codecs.open(dest, mode='w', encoding='utf-8') as f:
            f.write(result)
    else:
        return result
