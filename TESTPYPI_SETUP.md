# TestPyPI API Token Setup

To publish to TestPyPI, you'll need to create an API token:

1. Go to https://test.pypi.org/manage/account/ and log in
2. Scroll down to the "API tokens" section
3. Click "Add API token"
4. Give it a name like "flvmeta-timestamp-analyzer-test"
5. Set the scope to "Upload packages to testpypi"
6. Click "Add token"
7. Copy the generated token (you won't see it again)

Then, replace the placeholder in `.pypirc`:
- Replace `YOUR_TEST_PYPI_API_TOKEN` with your actual TestPyPI API token

For example:
```
[testpypi]
repository: https://test.pypi.org/legacy/
username: __token__
password: pypi-AgEIcHRlc3QucHlwaS5vcmc...
```

After updating the `.pypirc` file, try uploading again:
```bash
twine upload --repository testpypi dist/*
```