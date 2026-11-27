#!/usr/bin/env bash
set -euo pipefail
if [[ -x /tmp/blender/blender ]]; then /tmp/blender/blender --version; exit 0; fi
name=blender-4.5.3-linux-x64.tar.xz
ok=0
for base in https://mirror.blender.org/release/Blender4.5 https://download.blender.org/release/Blender4.5; do
  rm -f /tmp/blender.tar.xz
  if curl --fail --location --retry 3 --retry-delay 3 --connect-timeout 25 --max-time 480 --silent --show-error "$base/$name" -o /tmp/blender.tar.xz && [[ "$(stat -c%s /tmp/blender.tar.xz)" == 377397328 ]] && xz -t /tmp/blender.tar.xz; then
    ok=1; break
  fi
done
[[ "$ok" == 1 ]] || { echo 'Official Blender download unavailable or incomplete'; exit 1; }
mkdir -p /tmp/blender
tar -xJf /tmp/blender.tar.xz --strip-components=1 -C /tmp/blender
/tmp/blender/blender --version
