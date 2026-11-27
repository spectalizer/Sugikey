# Contributing

## Releasing a new version

Releases are made from `main` with
[python-semantic-release](https://python-semantic-release.readthedocs.io/),
which picks the version bump from the commit messages since the last release
(`fix:` → patch, `feat:` → minor, breaking change → major).

```bash
poetry run semantic-release version   # works out the bump from feat:/fix: commits, updates version + CHANGELOG, commits, tags, pushes
poetry run twine upload dist/*        # upload to PyPI
```

`semantic-release version` also builds the package into `dist/`. Before
uploading, make sure `dist/` holds only the new version's files.
