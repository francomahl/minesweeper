from rest_framework.decorators import detail_route, list_route
from api.models import Game
from django.contrib.auth.models import User
from rest_framework import viewsets
from api.serializers import *
from rest_framework.response import Response
from rest_framework import permissions
from api.permissions import IsOwnerOrReadOnly
from django.shortcuts import get_object_or_404


class GameViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    def list(self, request):
        queryset = Game.objects.all()
        serializer = GameSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Game.objects.all()
        game = get_object_or_404(queryset, pk=pk)
        serializer = GameSerializer(game)
        return Response(serializer.data)

    def get_object(self, pk):
        return get_object_or_404(Game, pk=pk)

    @detail_route(methods=['get'])
    def state(self, request, pk=None):
        game = self.get_object(pk)
        serializer = GameSerializer(game, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['post'])
    def new(self, request, *args, **kwargs):
        serializer = GameNewSerializer(data=request.data)
        game = None
        player = self.request.user
        if serializer.is_valid(raise_exception=True):
            rows = serializer.validated_data['rows']
            columns = serializer.validated_data['columns']
            mines = serializer.validated_data['mines']
            game = Game()
            game.title = 'Game for user %s' % player.username
            board, player_board = Game.new_boards(rows, columns, mines)
            game.board = board
            game.player_board = player_board
            game.state = Game.STATE_NEW
            game.player = player
            game.save()
        serializer = GameSerializer(game, context={'request': request})
        return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
