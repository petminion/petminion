set -e

echo "Copying to development device (FIXME currently hardwired to geeksville's usage, please send in fixes to this file for your environment)"

# Where is our script? from https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ssh petminion1 -t "mkdir -p development"
rsync -av --exclude={'minionenv','*.pt','*.pth','.git'} $SCRIPT_DIR/.. petminion1:development/petminion