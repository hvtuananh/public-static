# coding: utf-8

import codecs
import re
import os
from datetime import datetime
from publicstatic import conf
from publicstatic import const
from publicstatic import helpers
from publicstatic import logger
from publicstatic.urlify import urlify

# format for the post source files
POST_NAME_FORMAT = "{year}{month}{day}-{name}.md"

# regular expression to extract {name} from a base name of post source file
RE_POST_NAME = re.compile(r"^[\d_-]*([^\.]*)", re.U)


class NotImplementedException(Exception):
    pass


class PageExistsException(Exception):
    pass


class SourceFile:
    """Basic abstraction used for static files to be copied w/o processing."""
    def __init__(self, file_name):
        self._path = os.path.join(self.source_dir(), file_name)
        self._rel_path = os.path.relpath(self._path, self.source_dir())
        self._ext = os.path.splitext(file_name)[1].lower()
        self._ctime = datetime.fromtimestamp(os.path.getctime(self._path))
        self._utime = datetime.fromtimestamp(os.path.getmtime(self._path))
        self._processed = False
        self._rel_dest = None

    def __str__(self):
        """Human-readable string representation."""
        return '\n'.join(["%s: %s" % (k, v) for k, v in [
                ('class', self.__class__),
                ('fullname', self._path),
                ('created', self.created().isoformat()),
                ('updated', self.updated().isoformat()),
            ]])

    def source_dir(self):
        """Source file directory path."""
        raise NotImplementedException()

    def path(self):
        """Full path to the source file."""
        return self._path

    def rel_path(self):
        """Source file path relative to the source root directory."""
        return self._rel_path

    def basename(self):
        """Source file base name."""
        return os.path.basename(self._path)

    def ext(self):
        """Source file extension with leading dot."""
        return self._ext

    def rel_dest(self):
        """Get relative path to destination file."""
        return self._rel_dest

    def dest(self):
        """Returns fully qualified destination file."""
        return os.path.join(conf.get('build_path'), self.rel_dest())

    def dest_dir(self):
        """Returns fully qualified destination directory path."""
        return os.path.dirname(self.dest())

    def url(self, full=False):
        """Returns an URL corresponding to the source file."""
        root = conf.get('root_url') if full else conf.get('rel_root_url')
        return root + self.rel_dest()

    def created(self):
        return self._ctime

    def updated(self):
        return self._utime

    def processed(self, value=None):
        """Get/set 'processed' flag for the file."""
        if type(value) == bool:
            self._processed = value
        return self._processed

    def create():
        """Class function to create new source files of the certain type."""
        raise NotImplementedException()


class ParseableFile(SourceFile):
    """Basic abstraction for parseable source files."""

    # parse '<key>: <value>' string to (str, str) tuple
    _re_param = re.compile(r"^\s*([\w\d_-]+)\s*[:=]{1}(.*)", re.U)

    def __init__(self, file_name):
        super().__init__(file_name)
        self._data = self._parse()

    def data(self, key=None, default=None):
        """Returns page data as a dictionary, or a single data field
        if key argument specified."""
        return self._data.get(key, default) if key else self._data

    def text(self):
        """Source file contents."""
        if not hasattr(self, '_text'):
            with codecs.open(self._path, 'r', encoding='utf-8') as f:
                self._text = f.read()
        return self._text

    def created(self):
        return self.data('created')

    def updated(self):
        return self.data('updated')

    def default_template(self):
        raise NotImplementedException()

    def source_url(self):
        """Source file URL."""
        raise NotImplementedException()

    def _split(self):
        """Coarse parser for the source file."""
        result = {}
        lines = self.text().splitlines()
        num = 0
        for line in lines:
            match = ParseableFile._re_param.match(line)
            if match:
                field = match.group(1).strip().lower()
                result[field] = match.group(2).strip()
                num += 1
            else:
                break
        return result, ''.join(lines[num:])

    @staticmethod
    def _tags(value):
        """Parses tags from comma-separaed string, or returns default
        tags set from configuration."""
        tags = list(helpers.xsplit(',', value, strip=True, drop_empty=True))
        for tag in tags or conf.get('default_tags'):
            yield {'name': tag, 'url': helpers.tag_url(tag)}

    def _parse(self):
        """Extract page header data and content from a list of lines
        and return the result as key-value couples."""
        meta, content = self._split()
        meta.update({
                'source': self._path,
                'title':
                    meta.get('title', helpers.get_h1(content)),
                'template':
                    meta.get('template', self.default_template()),
                'author': meta.get('author', conf.get('author')),
                'tags': list(ParseableFile._tags(meta.get('tags', ''))),
                'source_url': self.source_url(),
                'created':
                    helpers.parse_time(meta.get('created'), self._ctime),
                'updated':
                    helpers.parse_time(meta.get('updated'), self._utime),
                'content':
                    helpers.md(content, conf.get('markdown_extensions')),
            })

        return meta


class AssetFile(SourceFile):
    def __init__(self, file_name):
        super().__init__(file_name)
        base = os.path.splitext(self._rel_path)[0]
        ext = '.css' if self.ext() == '.less' else self.ext()
        self._rel_dest = base + ext

    def source_dir(self):
        return conf.get('assets_path')


class PageFile(ParseableFile):
    def __init__(self, file_name):
        super().__init__(file_name)
        base = os.path.splitext(self._rel_path)[0]
        ext = '.html' if self.ext() in ['.md', '.markdown'] else self.ext()
        self._rel_dest = base + ext

    def source_dir(self):
        return conf.get('pages_path')

    def default_template(self):
        return conf.get('page_tpl')

    def source_url(self):
        """Source file URL."""
        pattern = "{root}blob/master/{type}/{name}"
        return pattern.format(root=conf.get('source_url'),
                              type='posts',
                              name=self.basename())

    @staticmethod
    def create(name, force=False):
        """Creates page file.

        Arguments:
            name -- page name (will be used for file name and URL).
            force -- True to overwrite existing file;
                False to throw exception."""
        page_name = urlify(name, ext_map={ord(u'\\'): u'/'}) + '.md'
        file_name = os.path.join(conf.get('pages_path'), page_name)
        if os.path.exists(file_name) and not force:
            raise PageExistsException()

        created = datetime.now().strftime(conf.get('time_format')[0])
        text = helpers.prototype('default-page')
        helpers.newfile(file_name, text.format(title=name, created=created))
        return page_name


class PostFile(ParseableFile):
    def __init__(self, file_name):
        super().__init__(file_name)
        name = os.path.basename(self._rel_path).lstrip('0123456789-_')
        path = conf.get('post_location')
        created = self.created()
        self._rel_dest = path.format(year=created.strftime('%Y'),
                                     month=created.strftime('%m'),
                                     day=created.strftime('%d'),
                                     name=os.path.splitext(name)[0])

    def source_dir(self):
        return conf.get('posts_path')

    def name(self):
        base, ext = os.path.splitex(os.path.basename(self._rel_path))
        return

    def default_template(self):
        return conf.get('post_tpl')

    def source_url(self):
        """Source file URL."""
        root = conf.get('source_url')
        if not root:
            return None
        pattern = "{root}blob/master/{type}/{name}"
        return pattern.format(root=conf.get('source_url'),
                              type='pages',
                              name=self.basename())

    @staticmethod
    def create(name, force=False):
        """Create new post file placeholder with a unique name.

        Arguments:
            name -- post name.
            force -- True to overwrite existing file;
                False to raise an exception."""
        created = datetime.now()
        post_name = urlify(name) or const.UNTITLED_POST
        file_name = POST_NAME_FORMAT.format(year=created.strftime('%Y'),
                                            month=created.strftime('%m'),
                                            day=created.strftime('%d'),
                                            name=post_name)
        post_path = os.path.join(conf.get('posts_path'), file_name)

        count = 1
        while True:
            file_name = helpers.suffix(post_path, count)
            if force or not os.path.exists(file_name):
                created = created.strftime(conf.get('time_format')[0])
                text = helpers.prototype('default-post')
                text = text.format(title=name, created=created)
                helpers.newfile(file_name, text)
                break
            count += 1
        return os.path.basename(file_name)
