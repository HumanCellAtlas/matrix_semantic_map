from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(name='matrix_semantic_map',  # Required
      version='v0.0.1',  # Required

      # This is a one-line description or tagline of what your project does. This
      # corresponds to the "Summary" metadata field:
      # https://packaging.python.org/specifications/core-metadata/#summary
      description='Semantic mapper for Loom file metadata.',  # Optional)
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='David Osumi-Sutherland',  # Optional

      # This should be a valid email address corresponding to the author listed
      # above.
      author_email='',  # Optional
      package_data={  # Optional
          'matrix_semantic_map': ['json_schema/expression_matrix_semantic_map.json'],
      },

      # Classifiers help users find your project by categorizing it.
      #
      # For a list of valid classifiers, see https://pypi.org/classifiers/
      classifiers=[  # Optional
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 4 beta',
          # Indicate who your project is intended for
          'Intended Audience :: single cell RNAseq data scientists',
          # Pick your license as you wish
          'License :: Apache 2.0',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
      ],
      project_urls={  # Optional
          'Bug Reports': 'https://github.com/HumanCellAtlas/matrix_semantic_map/issues',
          'Source': 'https://github.com/HumanCellAtlas/matrix_semantic_map/',
      },
      )
