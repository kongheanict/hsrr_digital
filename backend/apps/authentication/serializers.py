from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def get_token(self, user):
        token = super().get_token(user)
        token['role'] = user.role  # Add role to payload
        token['fullname'] = user.first_name + ' ' + user.last_name  # Add full name to payload
        return token