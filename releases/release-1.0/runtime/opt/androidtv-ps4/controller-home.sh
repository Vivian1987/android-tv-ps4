#!/bin/sh
set -eu
for file in /android/system/usr/keylayout/Vendor_054c_Product_*.kl /android/system/product/usr/keylayout/Vendor_054c_Product_*.kl; do
 [ -f "$file" ] || continue
 if grep -q 'BUTTON_MODE' "$file"; then
  sed 's/BUTTON_MODE/HOME/g' "$file" > /run/ps4-controller-layout
  cat /run/ps4-controller-layout > "$file"
 fi
done
rm -f /run/ps4-controller-layout
