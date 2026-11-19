#!/usr/bin/env bash
# Cloudflare Pages build for franksandbuns.com.
# Cloudflare's build command runs this file; edit it here (not in the dashboard)
# whenever the site gets new kinds of files or folders.
set -euo pipefail

rm -rf dist
mkdir -p dist

# Site pages, images, scripts and config files at the top level
cp *.html *.png *.jpg *.ico *.js ads.txt robots.txt sitemap.xml _headers dist/

# Game sound files (WAV effects, intro, music) and their attribution
if [ -d audio ]; then
  cp -R audio dist/
fi

echo "Build complete: $(find dist -type f | wc -l | tr -d ' ') files"
