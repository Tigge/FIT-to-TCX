for f in "$@" ; do python fittotcx.py "$f" > "${f%.fit}.tcx" ; done
