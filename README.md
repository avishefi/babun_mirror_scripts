# babun_mirror_scripts
Scripts for mirroring a Cygwin distribution for Babun build &amp; releases

1. `sync_mirror.sh` - downloads a remote Cygwin repository using rsync and GNU Parallel.
2. `validate_packages.py` - parses Cygwin setup.ini and validates all packages, produces a JSON file with package errors.
