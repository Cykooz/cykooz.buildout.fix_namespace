****************************
cykooz.buildout.fixnamespace
****************************

This buildout extension monkey-patch function
``zc.buildout.easy_install.make_egg_after_pip_install``
and ``zc.buildout.easy_install.Installer._get_dist``
to create file ``namespace_packages.txt`` for some packages with
native namespaces (`PEP-420 <https://peps.python.org/pep-0420/>`_)
which doesn't have it.

Minimal usage example::

    [buildout]
    extensions = cykooz.buildout.fix_namespace

