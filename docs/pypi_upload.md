=================================
Updating resync-simulator on pypi
=================================

Notes to remind zimeon...

resync-simulator is at https://pypi.python.org/pypi/resync-simulator

Putting up a new version
------------------------

0. In dev branch: check version number in simulator/_version.py and CHANGES.md are up to date
1. Check all tests good (python setup.py test; py.test)
2. Check branches as expected (git branch -a)
3. Merge to master
4. Check local build and version reported OK (python setup.py build; python setup.py install)
5. Check simulator works: run and check on web at http://localhost:8888/ and follow links
6. Check by harvesting with resync client
7. If all checks out OK, tag and push the new version to github:

    ```
    git tag -n1
    #...current tags
    git tag -a -m "ResourceSync Simulator v1.0.1, v1.0 specification, using v1.0.2 resync library" v1.0.1
    git push --tags

8. Upload to PyPI

```
rm -r dist
python setup.py sdist bdist_wheel; ls dist
# Should be source and wheel files for just this version
twine upload dist/*
```

9. Then check on PyPI at https://pypi.python.org/pypi/resync-simulator
10. Finally, back on develop branch start new version number by editing simulator/_version.py and CHANGES.md

