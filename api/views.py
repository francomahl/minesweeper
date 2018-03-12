from rest_framework.decorators import detail_route, list_route
from api.models import Game
from django.contrib.auth.models import User
from rest_framework import viewsets
from api.serializers import *
from rest_framework.response import Response
from rest_framework import permissions
from api.permissions import IsOwnerOrReadOnly
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt


class GameViewSet(viewsets.ViewSet):
    """
    JSON API endpoint to process game requests through the following actions.

    - `ID/state/`: **Returns** the game object.
    - `new/`: Creates a new game. **Returns** the game state. Arguments:
        - rows (number of rows)
        - columns (number of columns)
        - mines (number of mines, should be less than the board size)
    - `ID/pause/`: Pauses a given game (stops time tracking). **Returns** the game state.
    - `ID/resume/`: Resumes a given game (starts time tracking). **Returns** the game state.
    - `ID/mark_as_flag/`: Set a flag mark in a given cell. **Returns** the game state. Arguments:
        - x (cell index)
        - y (cell index)
    - `ID/mark_as_question/`: Set a question mark in a given cell. **Returns** the game state. Arguments:
        - x (cell index)
        - y (cell index)
    - `ID/reveal/`: Reveals a given cell. **Returns** the game state. Arguments:
        - x (cell index)
        - y (cell index)

    The current `state` can be:

    - **new** : for a new game.
    - **started** : if the game is running.
    - **paused** : if the game is paused.
    - **timeout** : if the game finished by timeout.
    - **won** : if the player won the game.
    - **lost** : if the player lost the game.

    The `board_view` is a matrix where each cell can be:

    - an empty character if the user hasn't set a mark or revealed the cell.
    - **?** : if the user set a question mark
    - **!** : if the user set a red flag mark
    - **x** : to indicate the cell has a mine.
    - an integer (0-8) to indicate the number of adjacent mines to the cell.

    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    @csrf_exempt
    def get(self, request, pk, format=None):
        queryset = Game.objects.all()
        game = get_object_or_404(queryset, pk=pk)
        serializer = GameSerializer(game)
        return Response(serializer.data)

    @csrf_exempt
    def list(self, request):
        queryset = Game.objects.all()
        serializer = GameSerializer(queryset, many=True)
        return Response(serializer.data)

    @csrf_exempt
    def get_object(self, pk):
        return get_object_or_404(Game, pk=pk)

    @csrf_exempt
    @detail_route(methods=['get'])
    def state(self, request, pk=None):
        game = self.get_object(pk)
        serializer = GameSerializer(game, context={'request': request})
        return Response(serializer.data)

    @csrf_exempt
    @list_route(methods=['get','post'])
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

    @csrf_exempt
    @detail_route(methods=['post'])
    def tick(self, request, pk=None):
        """Gets a clock tick from the client. Each tick represents a second passed by during the game.
        If duration_seconds gets to 0 then the game is over"""
        game = self.get_object(pk)
        game.duration_seconds -= 1
        if game.duration_seconds == 0:
            game.state = Game.STATE_TIMEOUT
        game.save()
        serializer = GameSerializer(game, context={'request': request})
        return Response(serializer.data)

    @csrf_exempt
    @detail_route(methods=['post'])
    def pause(self, request, pk=None):
        game = self.get_object(pk)
        game.state = Game.STATE_PAUSED
        game.save()
        serializer = GameSerializer(game, context={'request': request})
        return Response(serializer.data)

    @csrf_exempt
    @detail_route(methods=['post'])
    def resume(self, request, pk=None):
        game = self.get_object(pk)
        game.duration_seconds -= 1
        game.state = Game.STATE_STARTED
        game.save()
        serializer = GameSerializer(game, context={'request': request})
        return Response(serializer.data)

    @csrf_exempt
    @detail_route(methods=['post'])
    def mark_as_flag(self, request, pk=None):
        serializer = GameFieldSerializer(data=request.data)
        game = self.get_object(pk)
        if serializer.is_valid(raise_exception=True):
            x = serializer.validated_data['x']
            y = serializer.validated_data['y']
            game.mark_flag_at(x, y)
            game.save()
        serializer = GameSerializer(game, context={'request': request})
        return Response(serializer.data)

    @csrf_exempt
    @detail_route(methods=['post'])
    def mark_as_question(self, request, pk=None):
        serializer = GameFieldSerializer(data=request.data)
        game = self.get_object(pk)
        if serializer.is_valid(raise_exception=True):
            x = serializer.validated_data['x']
            y = serializer.validated_data['y']
            game.mark_question_at(x, y)
            game.save()
        serializer = GameSerializer(game, context={'request': request})
        return Response(serializer.data)

    @csrf_exempt
    @detail_route(methods=['post'])
    def reveal(self, request, pk=None):
        serializer = GameFieldSerializer(data=request.data)
        game = self.get_object(pk)
        if serializer.is_valid(raise_exception=True):
            x = serializer.validated_data['x']
            y = serializer.validated_data['y']
            game.reveal_at(x, y)
            if game.is_mine_at(x, y):
                game.state = Game.STATE_LOST
            elif game.is_all_revealed():
                game.state = Game.STATE_WON
            game.save()
        serializer = GameSerializer(game, context={'request': request})
        return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
