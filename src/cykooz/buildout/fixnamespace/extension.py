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
        "and zc.buildout.easy_install.Installer._get_dist "
        "to create file namespace_packages.txt for some packages with native "
        "namespaces which doesn't have this file."
    )

    orig_make_egg_after_pip_install = easy_install.make_egg_after_pip_install
    orig_get_dist = easy_install.Installer._get_dist

    def make_egg_after_pip_install(dest, distinfo_dir):
        fix_namespace_packages_txt(dest, distinfo_dir)
        return orig_make_egg_after_pip_install(dest, distinfo_dir)

    def _get_dist(self, *args, **kwargs):
        dists = orig_get_dist(self, *args, **kwargs)
        for dist in dists:
            dist_path = Path(os.path.normpath(dist.location))
            fix_namespace_packages_txt(dist_path, 'EGG-INFO')
            create_namespace_init(dist_path, 'EGG-INFO')
        return dists

    easy_install.make_egg_after_pip_install = make_egg_after_pip_install
    easy_install.Installer._get_dist = _get_dist


def fix_namespace_packages_txt(dest, distinfo_dir: str):
    dest = Path(dest)
    distinfo_dir = dest / distinfo_dir
    if not distinfo_dir.is_dir():
        return
    namespace_packages_file = distinfo_dir / 'namespace_packages.txt'
    if namespace_packages_file.is_file():
        return

    top_level_file = distinfo_dir / 'top_level.txt'
    if top_level_file.is_file():
        with top_level_file.open('rt') as f:
            top_levels = filter(
                lambda x: len(x) > 0,
                (line.strip() for line in f.readlines())
            )
    else:
        top_levels = []
        for entry in os.scandir(dest):
            if not entry.is_dir():
                continue
            path = Path(entry.path)
            if path == distinfo_dir:
                continue
            for _, _, file_names in os.walk(path):
                if any(
                        name.endswith(('.py', '.pyc', '.pyo', '.pyd'))
                        for name in file_names
                ):
                    top_levels.append(entry.name)
                    break

    namespaces = set()
    for top_level in top_levels:
        top_dir = dest / top_level
        if not top_dir.is_dir():
            continue
        namespaces.update(n for n in get_namespaces(top_dir) if n)
    if namespaces:
        namespaces = sorted(namespaces)
        with namespace_packages_file.open('wt') as f:
            for namespace in namespaces:
                f.write(namespace + '\n')


def get_namespaces(root_dir: Path):
    dir_names, has_init = get_child_dirs(root_dir)
    if not dir_names:
        if has_init:
            return [None]
        return []
    namespaces = set()
    root_name = root_dir.name
    for dir_name in dir_names:
        child_dir = root_dir / dir_name
        child_namespaces = get_namespaces(child_dir)
        for namespace in child_namespaces:
            if namespace is None:
                namespaces.add(root_name)
            else:
                namespaces.add(f'{root_name}.{namespace}')
    if namespaces:
        namespaces.add(root_name)
    return sorted(namespaces)


def get_child_dirs(path: Path) -> tuple[list[str], bool]:
    init_path = path / '__init__.py'
    has_init = init_path.is_file()
    if has_init:
        return [], True
    dirs = []
    for name in os.listdir(path):
        p = path / name
        if p.is_file():
            return [], False
        elif p.is_dir():
            dirs.append(name)
    return dirs, False


NAMESPACE_PACKAGE_INIT = "__import__('pkg_resources').declare_namespace(__name__)\n"


def create_namespace_init(dest: Path, distinfo_dir: str):
    namespace_packages_file = dest / distinfo_dir / 'namespace_packages.txt'
    if namespace_packages_file.is_file():
        with namespace_packages_file.open() as f:
            namespace_packages = [
                line.strip().replace('.', os.path.sep)
                for line in f.readlines()
            ]

        for namespace_package in namespace_packages:
            namespace_package_dir = dest / namespace_package
            if namespace_package_dir.is_dir():
                init_py_file = namespace_package_dir / '__init__.py'
                if not init_py_file.is_file():
                    with open(init_py_file, 'w') as f:
                        f.write(NAMESPACE_PACKAGE_INIT)
