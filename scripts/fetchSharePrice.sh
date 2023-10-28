#! /usr/bin/env bash

curl https://www.dsebd.org/latest_share_price_scroll_l.php -s | python -m sed_parser --site dse --page-type sharePrice --format csv > "dumps/dse/share_price/$(date +"%Y-%m-%d").csv"
