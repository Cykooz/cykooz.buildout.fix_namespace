# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 14.04.2020
"""

def runtests():
    import sys
    import pytest
    from pathlib import Path
    root_dir_path = Path(__file__).parent / '..' / '..' / '..' / '..'
    cfg_path = root_dir_path / 'src' / 'setup.cfg'

    args = sys.argv[1:]
    if not args or args[0].startswith('-'):
        args += ['--pyargs', 'cykooz.buildout.fixnamespace']
    args = [
               '-c', str(cfg_path),
               '--rootdir', str(root_dir_path),
           ] + args

    return pytest.main(args)
