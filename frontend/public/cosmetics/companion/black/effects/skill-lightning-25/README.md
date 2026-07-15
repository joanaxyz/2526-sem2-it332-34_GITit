black:

init - charge (f: 1 - 8) -> fly (f: 9 - 14) -> impact(ground) (f: 15 - 25)

clone - fly (f: 1 - 15) -> impact(center) (f: 16 - 25)

status - target-center

config - target-center

log - target-center

show - target-ground

diff - charge (f: 1 - 8) -> fly (f: 9 - 14) -> impact(center) (f: 15 - 25)

add - charge (f: 1 - 3) -> fly (f: 4 - 18) -> impact(center) (f: 19 - 25)

commit - target-ground

rm - charge (f: 1 - 5) -> fly (f: 6 - 17) -> impact(center) (f: 18 - 25)

check-ignore - target-ground

restore - target-ground

branch - charge (f: 1 - 4) -> fly (f: 5 - 19) -> impact(center) (f: 20 - 25)

switch - ground-run

checkout - charge (f: 1 - 3) -> fly (f: 4 - 17) -> impact(center) (f: 18 - 25)

merge - fly (f: 1 - 20) -> impact(center) (f: 21 - 25)

merge-base_front - target-ground

merge-base_back - target-ground

checkout-conflict - target-center

diff-conflict - target-ground

ls-files - target-ground

mergetool - target-center

reset - target-ground

revert - target-center

reflog - charge (f: 1 - 10) -> fly (f: 11 - 16) -> impact(center) (f: 17 - 25)

stash - charge (f: 1 - 2) -> fly (f: 3 - 15) -> impact(center) (f: 16 - 25)

cherry-pick_front - target-ground

cherry-pick_back - target-ground

remote_front - target-ground

remote_back - target-ground

fetch - target-center

pull - target-ground

push - ground-run

rebase - target-ground

default - charge (f: 1 - 6) -> fly (f: 7 - 15) -> impact(center) (f: 16 - 25)

crop-repairs:

diff-conflict - removed raw cross-cell top slice (f: 11, 16 - 25)
