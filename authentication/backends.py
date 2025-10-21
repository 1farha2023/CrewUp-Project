from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        # Use case-insensitive lookup and avoid get() which can raise MultipleObjectsReturned
        if username is None or password is None:
            return None

        # Try to find a matching user by username or email (case-insensitive)
        qs = UserModel.objects.filter(Q(username__iexact=username) | Q(email__iexact=username))
        user = qs.first()
        if user and user.check_password(password):
            return user
        return None