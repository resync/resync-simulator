=================================
Updating resync-simulator on pypi
=================================

Notes to remind zimeon...

resync-simulator is at https://pypi.python.org/pypi/resync-simulator

Putting up a new version
------------------------

0. In dev branch: bump version number in setup.py and check CHANGELOG is up to date
1. Check all tests good (python setup.py test; py.test)
2. Check code is up-to-date with github version
3. Check out master and merge in dev
4. Check all tests good (python setup.py test; py.test)
5. Check branches as expected (git branch -a)
6. Check local build and version reported OK (python setup.py build; sudo python setup.py install)
7. Check simulator works: run and check on web at http://localhost:8888/ and follow links
8. Check by harvesting with resync client
9. If all checks out OK, tag and push the new version to github:

    ```
    git tag -n1
    #...current tags
    git tag -a -m "ResourceSync Simulator, v0.9.3 specification for v0.9.3 resync library" v0.7
    git push --tags

    python setup.py sdist upload
    ```

10. Then check on PyPI at https://pypi.python.org/pypi/resync-simulator
11. Finally, back on dev branch start new version number by editing setup.py and CHANGELOG

