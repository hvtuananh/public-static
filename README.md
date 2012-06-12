# public-static

A small Python script used to build single-page¹ static website from [Markdown](http://daringfireball.net/projects/markdown) source, [Mustache](http://mustache.github.com) template and [Skeleton](http://getskeleton.com) CSS framework. Created ~~to maintain author's homepage~~ for fun. Inspired by [addmeto.cc](https://github.com/bobuk/addmeto.cc) and couple of other geeky projects.

¹ — two pages will be Ok too.

## Usage

Command line format:

	python ps.py <command> [parameters]

Available commands:

* `build` — generate web content.
* `preview` — run local web server to preview generated web site.

	* `-b` or `--browse` — opens site preview in default browser (disabled by default).
	* `-p` or `--port=HTTP-PORT` — save script output to log file (default value is 8000).

* `publish` — synchronize remote web server with generated content.
* `clean` — delete all generated web content.

Common parameters:

* `-c` or `--config=CONFIG` — specify configuration file. Default is `ps.ini`.
* `-s` or `--section=SECTION` — specify configuration file section. Default is the first one in the file.
* `-l` or `--logfile=LOGFILE` — save script output to log file.
* `-h` or `--help` — show command line help.

## Configuration file

To avoid over-complicated command line syntax, main site building parameters intended to be kept in configuration file with an ordinary [RFC-822](http://tools.ietf.org/html/rfc822.html) compliant syntax. As it was mentioned already default section name is `builder` but a single 
configuration file could contain multiple sections for different web sites to be maintained.

* `pages_path` — path to the page files directory.
* `static_path` — path to static resources (graphics, JS, CSS, etc) which should be copied to the generated website as is. JS and CSS files could be optionally minified (see details below).
* `templates_path` — [mustache](http://mustache.github.com) templates directory path.
* `build_path` — destination path where static website should be built.
* `minify_css` — yes/no to enable or disable CSS minification.
* `minify_js` — same thing for JavaScript.
* `run_browser_cmd` — OS-specific command to open an URL with a web browser. Used during generated website preview.
* `browser_opening_delay` — number of seconds between preview webserver start and browser execution. Default value is 2.0 and it's
 
Example:

	[ps]
	pages_path = ./pages
	static_path = ./static
	build_path = ./www
	templates_path = ./templates
	minify_css = yes
	minify_js = yes
	run_browser_cmd = start {url}
	browser_opening_delay = 2

## Page file format

Each page is a plain text/markdown file complemented with a basic metadata in header. The format is pretty straightforward. Here is a self explaining example:

	title: Hello World!
	ctime: 2012-06-05 13:49:38
	mtime: 2012-06-05 13:49:38
	template: default

	# Hello world!

	The format is pretty straightforward.

Few comments:

* All header fields are optional and could omitted. But it's good to have at least a title for each page.
* Template value will be transformed to `[templates_path]\[template_name].mustache.html` file name`.
* All matadata parameters are available from templates. E.g. `{{title}}`.
* Everything beneath the header is treated as page content. Template name for this section is `{{content}}`.

## Dependencies

* `baker`
* `python-markdown`
* `pystache`
* `yuicompressor`

# TODO

* Implement synchronization.
* Validate configuration.

# Changes

* 2012-06-10 — The first configuration file section will be used as default instead of `[<script name>]`.
* 2012-06-10 — CSS/JS miminization with yuicompressor.
* 2012-06-09 — `build.py` renamed to `ps.py`. Default section renamed to `[ps]`.