set -e

# Before running:
#add repository to poetry config
#poetry config repositories.test-pypi https://test.pypi.org/legacy/
#get token from https://test.pypi.org/manage/account/token/
#store token using poetry config pypi-token.test-pypi  pypi-YYYYYYYY

poetry publish -r test-pypi --build
