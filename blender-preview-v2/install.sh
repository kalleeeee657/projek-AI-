#!/usr/bin/env bash
set -euo pipefail
curl --fail --location --retry 4 --silent --show-error https://download.blender.org/release/Blender4.5/blender-4.5.3-linux-x64.tar.xz -o /tmp/blender.tar.xz
mkdir -p /tmp/blender
tar -xJf /tmp/blender.tar.xz --strip-components=1 -C /tmp/blender
/tmp/blender/blender --version
