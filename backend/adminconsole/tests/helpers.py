"""Small factories shared by admin console API tests."""


def make_user(django_user_model, username="player", *, is_staff=False):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
        is_staff=is_staff,
    )
