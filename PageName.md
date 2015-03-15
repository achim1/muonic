# Uploading dist files to pypi #

To upload a new muonic version to the python package index, you have to
  * increase the version number in `setup.py`
  * **optional**: run `python setup.py register`
  * and finally run `python setup.py bdist_egg sdist upload`

The last step will build `*.egg` and `*.tar.gz` files and upload them