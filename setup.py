from setuptools import setup, find_packages
from os import path
import glob

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(name='matrix_semantic_map',  # Required
      version='v0.0.3',  # Required

      # This is a one-line description or tagline of what your project does. This
      # corresponds to the "Summary" metadata field:
      # https://packaging.python.org/specifications/core-metadata/#summary

      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      py_modules=[path.splitext(path.basename(path))[0] for path in glob.glob('src/*.py')],
      include_package_data=True,
      description='Semantic mapper for Loom file metadata.',  # Optional)
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='David Osumi-Sutherland',  # Optional
      url='https://github.com/HumanCellAtlas/matrix_semantic_map/',
      # This should be a valid email address corresponding to the author listed
      # above.
      author_email='dosumis@gmail.com',  # Optional
      data_files=[('json_schema', ['src/json_schema/expression_matrix_semantic_map.json'])],

      # Classifiers help users find your project by categorizing it.
      #
      # For a list of valid classifiers, see https://pypi.org/classifiers/
      classifiers=[  # Optional
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 4 - Beta',
          # Indicate who your project is intended for
          # Pick your license as you wish
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3',
      ],
      project_urls={  # Optional
          'Bug Reports':'https://github.com/HumanCellAtlas/matrix_semantic_map/issues',
          'Source':'https://github.com/HumanCellAtlas/matrix_semantic_map/src',
      },
      )
