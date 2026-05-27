from rest_framework import serializers

from .models import User, Preview


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['email', 'name', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class PreviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Preview
        fields = [
            'id', 'user', 'user_name', 'url',
            'title', 'description', 'image_url', 'raw_text',
            'created_at',
        ]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class PreviewCreateSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=2000)
    title = serializers.CharField(max_length=500, required=False, allow_blank=True, default='')
    description = serializers.CharField(max_length=2000, required=False, allow_blank=True, default='')
