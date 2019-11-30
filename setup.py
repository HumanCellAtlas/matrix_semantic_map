from setuptools import setup, find_packages
from os import path
import glob

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(name='matrix_semantic_map',  # Required
      version='v0.0.4',  # Required
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
      classifiers=[  # Optional
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3',
      ],
      project_urls={  # Optional
          'Bug Reports':'https://github.com/HumanCellAtlas/matrix_semantic_map/issues',
          'Source':'https://github.com/HumanCellAtlas/matrix_semantic_map/src',
      },
      )
