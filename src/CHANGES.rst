..  Changelog format guide.
    - Before make new release of core egg you MUST add here a header for new version with name "Next release".
    - After all headers and paragraphs you MUST add only ONE empty line.
    - At the end of sentence which describes some changes SHOULD be identifier of task from our task manager.
      This identifier MUST be placed in brackets. If a hot fix has not the task identifier then you
      can use the word "HOTFIX" instead of it.
    - At the end of sentence MUST stand a point.

CHANGELOG
*********

2.0.4 (2023-09-05)
==================

- Added support of packages without ``top_level.txt`` file.

2.0.2 (2023-09-03)
==================

- Fixed error.

2.0.0 (2023-09-03)
==================

- Added fix that creates ``namespace_packages.txt`` for some packages with
  native namespaces which doesn't have it.
- Removed fix of content of namespace ``__init__.py`` file.

1.0 (2020-04-14)
================

- Initial release.
