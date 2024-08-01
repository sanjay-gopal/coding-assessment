
## Unit tests
Install test dependencies:
```
pip3 install pytest pytest-json-report httpx
```

Now run the tests:
```
pytest test.py --json-report --json-report-file=report.json --json-report-indent=4
```

A nasty trick to get the modules loading correctly.
```
ln -s .devmatch/test.py test.py
```

