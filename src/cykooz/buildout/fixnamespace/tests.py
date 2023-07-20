# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 14.04.2020
"""
import os

import shutil

from .extension import get_namespaces, fix_namespace_packages_txt


def test_fix_namespaces(tmp_path):
    root_dir = tmp_path / 'root'
    root_dir.mkdir()

    # No files and dirs
    assert list(get_namespaces(root_dir)) == []

    sub1 = root_dir / 'sub1'
    sub1.mkdir()
    # One sub dir without files and dirs
    assert list(get_namespaces(root_dir)) == []

    sub1_init = sub1 / '__init__.py'
    sub1_init.open('wt').close()
    # One sub dir with file
    assert list(get_namespaces(root_dir)) == ['root']

    sub2 = root_dir / 'sub2'
    sub2.mkdir()
    # One sub dir with file and one without
    assert list(get_namespaces(root_dir)) == ['root']

    sub3 = sub2 / 'sub3'
    sub3.mkdir()
    # One sub dir with file and two without
    assert list(get_namespaces(root_dir)) == ['root']

    sub3_init = sub3 / '__init__.py'
    sub3_init.open('wt').close()
    assert list(get_namespaces(root_dir)) == ['root.sub2', 'root']

    sub4 = sub2 / 'sub4'
    sub4.mkdir()
    sub5 = sub4 / 'sub5'
    sub5.mkdir()
    sub5_init = sub5 / '__init__.py'
    sub5_init.open('wt').close()
    assert list(get_namespaces(root_dir)) == [
        'root.sub2',
        'root.sub2.sub4',
        'root'
    ]

    distinfo_dir = 'root.sub2-1.0.dist-info'
    info_dir = tmp_path / distinfo_dir
    info_dir.mkdir()
    toplevel_file = info_dir / 'top_level.txt'
    with toplevel_file.open('wt') as f:
        f.write('root\n')
        f.write('scripts\n')

    fix_namespace_packages_txt(tmp_path, distinfo_dir)
    namespace_packages_file = info_dir / 'namespace_packages.txt'
    assert namespace_packages_file.is_file()
    with namespace_packages_file.open('rt') as f:
        namespaces = [s.strip() for s in f.readlines()]
    assert namespaces == [
        'root',
        'root.sub2',
        'root.sub2.sub4',
    ]

    shutil.rmtree(sub2)
    root_init = root_dir / '__init__.py'
    root_init.open('wt').close()
    os.remove(namespace_packages_file)
    fix_namespace_packages_txt(tmp_path, distinfo_dir)
    assert not namespace_packages_file.is_file()
