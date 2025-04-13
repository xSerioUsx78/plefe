from rest_framework import serializers
from utils.time import custom_timesince
from .models import Log, LogDetail

class LogSerializer(serializers.ModelSerializer):

    from users.serializers import UserGlobalSerializer
    user = UserGlobalSerializer()
    created_at = serializers.DateTimeField(format='%Y/%m/%d - %H:%M:%S')
    created_at_timesince = serializers.SerializerMethodField()
    details_count = serializers.IntegerField()

    class Meta:
        model = Log
        fields = (
            'id',
            'user',
            'ip_address',
            'category', 
            'action',
            'badge',
            'title',
            'description',
            'created_at',
            'created_at_timesince',
            'details_count'
        )
    
    def get_created_at_timesince(self, obj):
        if obj:
            return custom_timesince(obj.created_at)
        return obj


class LogDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = LogDetail
        fields = '__all__'


# class LogEventSerializer(serializers.ModelSerializer):

#     from users.serializers import UserGlobalSerializer
#     user = UserGlobalSerializer()
#     created_at = serializers.DateTimeField(format='%Y/%m/%d - %H:%M:%S')
#     created_at_timesince = serializers.SerializerMethodField()
#     pgh_created_at = serializers.DateTimeField(format='%Y/%m/%d - %H:%M:%S')
#     pgh_created_at_timesince = serializers.SerializerMethodField()

#     class Meta:
#         model = LogEvent
#         fields = '__all__'

#     def get_created_at_timesince(self, obj):
#         if obj:
#             return custom_timesince(obj.created_at)
#         return obj
    
#     def get_pgh_created_at_timesince(self, obj):
#         if obj:
#             return custom_timesince(obj.pgh_created_at)
#         return obj