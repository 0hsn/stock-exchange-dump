#! /usr/bin/env bash

cd storage/ || exit
curl "https://www.dsebd.org/latest_share_price_scroll_l.php" -s -o "latest_share_price_scroll_l-$(date +"%Y%m%d").html"
cd - || exit
