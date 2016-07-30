from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated

from accounts.models import Kid
from accounts.serializers.kid_serializer import KidSerializer


class KidViewSet(viewsets.ModelViewSet):
    queryset = Kid.objects.all()
    serializer_class = KidSerializer
    permission_classes = (IsAuthenticated,)

    @list_route(methods=['POST'])
    def save(self, request):
        if 'id' in request.data:
            return self.update(request)
        return self.create(request)

    def create(self, request, *args, **kwargs):
        """
        Add kid
        @param request:
        @param args:
        @param kwargs:
        @return:
        ---
        parameters:
            - name: picture
              type: file
              required: true
        """
        return super(KidViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super(KidViewSet, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset
