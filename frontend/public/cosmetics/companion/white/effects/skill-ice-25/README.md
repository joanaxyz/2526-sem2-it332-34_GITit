white:

init - charge (f: 1 - 10) -> fly (f: 11 - 15) -> impact(ground) (f: 16 - 25)

clone - fly (f: 1 - 15) -> impact(center) (f: 16 - 25)

status - target-center

config - target-center

log - target-center

show - target-ground

diff - charge (f: 1 - 10) -> fly (f: 11 - 20) -> impact(center) (f: 21 - 25)

add - charge (f: 1 - 10) -> fly (f: 11 - 15) -> impact(center) (f: 16 - 25)

commit - target-ground

rm - fly (f: 1 - 16) -> impact(center) (f: 17 - 25)

check-ignore - target-ground

restore - target-ground

branch - charge (f: 1 - 2) -> fly (f: 3 - 17) -> impact(center) (f: 18 - 25)

switch - ground-run

checkout - charge (f: 1 - 10) -> fly (f: 11 - 20) -> impact(center) (f: 21 - 25)

merge - fly (f: 1 - 18) -> impact(ground) (f: 19 - 25)

merge-base - target-ground

checkout-conflict - target-center

diff-conflict - target-ground

ls-files - target-center

mergetool - target-center

reset - target-ground

revert - target-center

reflog - charge (f: 1 - 10) -> fly (f: 11 - 16) -> impact(center) (f: 17 - 25)

stash - fly (f: 1 - 13) -> impact(ground) (f: 14 - 25)

cherry-pick - target-ground

remote - target-ground

fetch - target-center

pull - target-ground

push - ground-run

rebase - target-ground

tag - target-ground

rev-list - target-center

default - charge (f: 1 - 10) -> fly (f: 11 - 15) -> impact(center) (f: 16 - 25)
