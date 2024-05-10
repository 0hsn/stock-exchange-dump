import sys
from datetime import datetime

st_ = 'Latest Share Price On '
in_ = str(sys.stdin.read())

ds_ = in_[in_.find(st_) + len(st_) : in_.find('</h2>', in_.find(st_) + len(st_))]
d_=datetime.strptime(ds_, '%b %d, %Y at %I:%M %p')

print(d_.strftime('%Y-%m-%d'))
