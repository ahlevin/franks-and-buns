#!/usr/bin/env bash
# Cloudflare Pages build for franksandbuns.com.
# Cloudflare's build command runs this file; edit it here (not in the dashboard)
# whenever the site gets new kinds of files or folders.
set -euo pipefail

rm -rf dist
mkdir -p dist

# Site pages, images, videos (how-to-play.mp4) and config files at the top level
cp *.html *.png *.jpg *.mp4 *.ico ads.txt robots.txt sitemap.xml llms.txt llms-full.txt _headers _redirects dist/

# AI-facing guide for agents (franksandbuns.com/AGENTS.md); kept in ai/ so coding tools don't read it as repo instructions
cp ai/AGENTS.md dist/AGENTS.md

# App links: lets Pack invite links (franksandbuns.com/join/CODE) open the iPhone and Android apps
cp -R .well-known dist/

# Videos page clips (videos.html)
if [ -d videos ]; then
  cp -R videos dist/
fi

# Social media videos (franksandbuns.com/social/, not linked from any page; Facebook/Instagram fetch them by URL)
if [ -d social ]; then
  cp -R social dist/
fi

# Game sound files (WAV effects, intro, music) and their attribution
if [ -d audio ]; then
  cp -R audio dist/
fi

echo "Build complete: $(find dist -type f | wc -l | tr -d ' ') files"
