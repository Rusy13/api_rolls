from django.db import models

class Roll(models.Model):
    id = models.AutoField(primary_key=True)
    length = models.BigIntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)
    date_deletion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Roll #{self.id}"