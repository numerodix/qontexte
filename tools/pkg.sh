#!/bin/bash

commit="$1"
pkgname="$(basename $(pwd))"

if [ ! "$commit" ]; then
	echo "Usage:  $0 <commit>"
	exit 1
fi

git archive --format tar --prefix "$pkgname/" $1 | gzip - > "$pkgname-$commit.tar.gz"
