"""Create or delete the load-test learners. Run through `manage.py shell -c` with PERF_ACTION set.

PERF_ACTION=create  -> creates perf01..perfNN (verified, never emailed), writes users + ids files
PERF_ACTION=delete  -> deletes exactly the ids recorded at creation (with everything they own)
PERF_ACTION=count   -> prints how many accounts and runs the recorded ids still own
"""
import json
import os
import secrets

from django.contrib.auth import get_user_model
from django.db import transaction

from accounts.services.core import UserService
from accounts.services.verification import EmailVerificationService

OUT = os.environ["PERF_OUT"]
COUNT = int(os.environ.get("PERF_COUNT", "40"))
ACTION = os.environ["PERF_ACTION"]
User = get_user_model()
ids_path = f"{OUT}/prod_user_ids.json"

if ACTION == "create":
    names = [f"perf{i:02d}" for i in range(1, COUNT + 1)]
    clash = list(User.objects.filter(username__in=names).values_list("username", flat=True))
    if clash:
        raise SystemExit(f"refusing: usernames already exist: {clash}")
    created, lines = [], []
    with transaction.atomic():
        for name in names:
            password = "Lt-" + secrets.token_urlsafe(18)
            user = UserService().register_account(username=name, email=f"{name}@loadtest.invalid", password=password)
            EmailVerificationService.mark_verified(user)
            created.append(user.id)
            lines.append(f"{name},{password}")
    open(ids_path, "w").write(json.dumps(created))
    open(f"{OUT}/prod_users.csv", "w").write("\n".join(lines) + "\n")
    print(f"created {len(created)} accounts")
elif ACTION == "delete":
    ids = json.load(open(ids_path))
    qs = User.objects.filter(id__in=ids, username__startswith="perf", email__endswith="@loadtest.invalid")
    n = qs.count()
    deleted = qs.delete()
    print(f"deleted {n} accounts; rows removed by model: {deleted[1]}")
elif ACTION == "count":
    ids = json.load(open(ids_path))
    from adventures.models import AdventureLevelTierRun
    print("accounts:", User.objects.filter(id__in=ids).count(),
          "| runs:", AdventureLevelTierRun.objects.filter(player__user_id__in=ids).count())
