from rest_framework import serializers
from .models import Roll


class RollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roll
        fields = ('id','length','weight','date_added','date_deletion')