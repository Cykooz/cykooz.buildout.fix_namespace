****************************
cykooz.buildout.fixnamespace
****************************

This buildout extension allows fix value of NAMESPACE_PACKAGE_INIT
constant from ``setuptools``. This value used to fix namespace packages
installed from wheels (https://github.com/pypa/setuptools/issues/2069).

Minimal usage example::

    [buildout]
    extensions = cykooz.buildout.fix_namespace

