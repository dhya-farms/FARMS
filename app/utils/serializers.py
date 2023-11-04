from django.conf import settings
from rest_framework import serializers


class EnumValueSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    name_vernacular = serializers.SerializerMethodField()
    icon_url = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_class = self.context.get('enum_class')
        self.field = self.context.get('field')

    def get_id(self, obj):
        return obj[0]  # First element of the tuple is the enum value

    def get_name(self, obj):
        enum = self.enum_class(obj[0])
        return enum.name  # Getting the enum instance name

    def get_name_vernacular(self, obj):
        return obj[1]  # Second element of the tuple is the human-readable name

    def get_icon_url(self, obj):
        enum = self.enum_class(obj[0])
        if self.field:
            return f"{settings.MEDIA_URL}icons/{self.field}/{enum.name.lower()}.svg"
        return None
