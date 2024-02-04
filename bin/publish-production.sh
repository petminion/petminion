set -e

# Before running:
#add repository to poetry config
#get token from https://pypi.org/manage/account/token/
#store token using poetry config pypi-token.pypi pypi-XXXXXXXX

poetry publish --build
