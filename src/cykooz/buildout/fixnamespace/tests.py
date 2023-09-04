# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 14.04.2020
"""
import os
from pathlib import Path

import pytest

from .extension import get_namespaces, fix_namespace_packages_txt


def _create_fs_tree(root_dir: Path, paths: list[str]):
    for path in paths:
        path = root_dir.joinpath(Path(path))
        if os.path.splitext(path.name)[1] == '.py':
            path.parent.mkdir(parents=True, exist_ok=True)
            path.open('wt').close()
        else:
            path.mkdir(parents=True, exist_ok=True)


@pytest.mark.parametrize(
    ['paths', 'result'],
    [
        ([], []),
        (['sub1'], []),
        (['sub1/__init__.py'], ['root']),
        (['sub1/sub2/__init__.py'], ['root', 'root.sub1']),
        (
                [
                    'sub1/__init__.py',
                    'sub2',
                ],
                ['root']
        ),
        (
                [
                    'sub1/__init__.py',
                    'sub2/sub3',
                ],
                ['root']
        ),
        (
                [
                    'sub1/__init__.py',
                    'sub2/sub3/__init__.py',
                ],
                ['root', 'root.sub2']
        ),
        (
                [
                    'sub1/__init__.py',
                    'sub2/sub3/__init__.py',
                    'sub2/sub4/sub5/__init__.py',
                ],
                ['root', 'root.sub2', 'root.sub2.sub4']
        ),
        (
                [
                    'sub1/__init__.py',
                    'sub2/sub3/__init__.py',
                    'sub4/sub5/readme.txt',
                ],
                ['root', 'root.sub2']
        ),
    ]
)
def test_fix_namespaces(tmp_path, paths, result):
    root_dir = tmp_path / 'root'
    root_dir.mkdir()
    _create_fs_tree(root_dir, paths)
    assert list(get_namespaces(root_dir)) == result

    distinfo_name = 'root.sub2-1.0.dist-info'
    distinfo_dir = tmp_path / distinfo_name
    distinfo_dir.mkdir()
    toplevel_file = distinfo_dir / 'top_level.txt'
    with toplevel_file.open('wt') as f:
        f.write('root\n')
        f.write('scripts\n')

    fix_namespace_packages_txt(tmp_path, distinfo_name)
    assert_namespace_packages(distinfo_dir, result)

    # Without top_level.txt
    os.remove(toplevel_file)
    np_path = distinfo_dir / 'namespace_packages.txt'
    if np_path.is_file():
        os.remove(np_path)
    fix_namespace_packages_txt(tmp_path, distinfo_name)
    assert_namespace_packages(distinfo_dir, result)


def assert_namespace_packages(distinfo_dir, result):
    namespace_packages_file = distinfo_dir / 'namespace_packages.txt'
    if result:
        assert namespace_packages_file.is_file()
        with namespace_packages_file.open('rt') as f:
            namespaces = [s.strip() for s in f.readlines()]
        assert namespaces == result
    else:
        assert not namespace_packages_file.is_file()
