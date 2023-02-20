# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'nasaaccess'
copyright = '2023, Ibrahim Mohammed, Giovanni Romero'
author = 'Ibrahim Mohammed, Giovanni Romero'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'press'
html_static_path = ['_static']
html_logo = '_static/github30x30.png'

html_sidebars = {'**': ['util/searchbox.html', 'util/sidetoc.html']}


html_theme_options = {
  "external_links": [
      ("Github", "https://github.com/imohamme/tethys_nasaaccess"),
      ("Email", "gromero@aquaveo.com")
  ]
}