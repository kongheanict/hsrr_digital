from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

class ValidateTokenView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"status": "valid"}, status=200)

class ServerTimeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"server_time": timezone.now()})