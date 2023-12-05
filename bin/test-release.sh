rm dist/*
set -e

#bin/regen-docs.sh
# pandoc --from=markdown --to=rst --output=README README.md
python3 -m build
python3 -m twine check dist/*
# test the upload
python3 -m twine upload --repository testpypi dist/*
echo "view the upload at https://test.pypi.org/project/petminion/ it it looks good upload for real"