# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 14.04.2020
"""
import logging
import os
from pathlib import Path

from zc.buildout import easy_install


def load_extension(buildout):
    logger = logging.getLogger('zc.buildout')
    logger.info(
        "Monkey-patching zc.buildout.easy_install.make_egg_after_pip_install "
        "to create file namespace_packages.txt for some packages with native "
        "namespaces which doesn't have it."
    )

    orig_make_egg_after_pip_install = easy_install.make_egg_after_pip_install

    def make_egg_after_pip_install(dest, distinfo_dir):
        fix_namespace_packages_txt(dest, distinfo_dir)
        return orig_make_egg_after_pip_install(dest, distinfo_dir)

    easy_install.make_egg_after_pip_install = make_egg_after_pip_install


def fix_namespace_packages_txt(dest, distinfo_dir):
    dest = Path(dest)
    distinfo_dir = dest / distinfo_dir
    namespace_packages_file = distinfo_dir / 'namespace_packages.txt'
    if namespace_packages_file.is_file():
        return

    top_level_file = distinfo_dir / 'top_level.txt'
    if top_level_file.is_file():
        with top_level_file.open('rt') as f:
            top_levels = filter(
                lambda x: len(x) != 0,
                (line.strip() for line in f.readlines())
            )
    else:
        top_levels = ()

    namespaces = []
    for top_level in top_levels:
        top_dir = dest / top_level
        if not top_dir.is_dir():
            continue
        namespaces.extend(get_namespaces(top_dir))
    if namespaces:
        namespaces.sort()
        with namespace_packages_file.open('wt') as f:
            for namespace in namespaces:
                f.write(namespace + '\n')


def get_namespaces(root_dir: Path):
    dir_names, has_init = get_child_dirs(root_dir)
    if not dir_names:
        if has_init:
            yield None
        return
    root_name = root_dir.name
    for dir_name in dir_names:
        child_dir = root_dir / dir_name
        child_namespaces = get_namespaces(child_dir)
        for namespace in child_namespaces:
            if namespace is None:
                yield root_name
            else:
                yield f'{root_name}.{namespace}'


def get_child_dirs(path: Path) -> tuple[list[str], bool]:
    dirs = []
    has_files = False
    has_init = False
    for name in os.listdir(path):
        p = path / name
        if p.is_file():
            has_files = True
            if name == '__init__.py':
                has_init = True
        elif p.is_dir():
            dirs.append(name)
    if has_files:
        return [], has_init
    return dirs, False
