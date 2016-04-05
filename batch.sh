for f in "$@" ; do fittotcx "$f" > "${f%.fit}.tcx" ; done
