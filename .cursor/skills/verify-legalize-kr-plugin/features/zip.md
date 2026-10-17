# Cowork upload ZIP

Consumer: Claude Cowork users who upload `legalize-kr-plugin.zip` from Releases.
Drive: `verify.sh zip`.
Pass: `valid: dist/legalize-kr-plugin.zip`.
Shape: the include list in `scripts/package_claude_plugin.py` is the only place to add a file. The validator derives its required set from it.
