#!/bin/bash
# v2.23.1: publish the smaller character images to franksandbuns.com (prepared by Claude, run from Finder)
cd ~/franks-and-buns || exit 1
set -e
git checkout main
git pull --ff-only origin main
cp small-images/chef.png small-images/chefarm.png small-images/dog.png small-images/dognodog.png small-images/hotdog.png .
python3 validate.py | tail -2
git add chef.png chefarm.png dog.png dognodog.png hotdog.png
git commit -m "v2.23.1: character images resized for fast loading on phones (8 MB to 130 KB)"
git tag v2.23.1-stable
git push origin main --tags
git checkout v1.1
echo
echo "DONE - v2.23.1 published. You can close this window."
