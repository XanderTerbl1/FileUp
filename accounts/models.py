from django.db import models
from django.contrib.auth.models import User


class UserPreferences(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # should this be dynamically calculated?
    # No... on upload/create of files/folder
    # determine who will be billed for it..
    # On delete determine who should be compensated
    current_usage_mb = models.DecimalField(
        default=0, decimal_places=2, max_digits=7)
    max_usage_mb = models.DecimalField(
        default=1000, decimal_places=2, max_digits=7, help_text="This value CAN'T be altered by normal users")

    recyclebin_lifetime = models.IntegerField(
        default=60, help_text="Recycle bin lifetime (days). Normal users may change this value.")

    def __str__(self):
        return self.user.username
