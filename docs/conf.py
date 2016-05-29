import os
import re


def get_version():
    docs_dir = os.path.dirname(__file__)
    proj_dir = os.path.dirname(docs_dir)
    version_file = os.path.join(proj_dir, 'log', '__version__.py')
    init_py = open(version_file).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


version = get_version()
release = version


extensions = [
    'sphinx.ext.autodoc',
]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = 'log'

copyright = '2016, Vince Forgione'

author = 'Vince Forgione'

language = 'en'

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'

todo_include_todos = False

html_static_path = ['_static']

htmlhelp_basename = 'logdoc'

latex_elements = {}

latex_documents = [
    (master_doc, 'log.tex', 'log Documentation',
     'Vince Forgione', 'manual'),
]

man_pages = [
    (master_doc, 'log', 'log Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, 'log', 'log Documentation',
     author, 'log', 'One line description of project.',
     'Miscellaneous'),
]


import sphinx_rtd_theme

html_theme = "sphinx_rtd_theme"

html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

autodoc_member_order = 'bysource'
