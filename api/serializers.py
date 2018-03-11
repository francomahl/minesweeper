from rest_framework import serializers
from api.models import Game
from django.contrib.auth.models import User
import json


class GameSerializer(serializers.ModelSerializer):
    board_view = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    player = serializers.ReadOnlyField(source='player.username')

    class Meta:
        model = Game
        fields = ('id', 'title', 'state', 'board_view',
                  'duration_seconds', 'player')

    def get_state(self, obj):
        return obj.get_state_display()

    def get_board_view(self, obj):
        view = []
        board = json.loads(obj.board)
        player_board = json.loads(obj.player_board)
        for i in range(len(board)):
            view_row = []
            for j in range(len(board[i])):
                if player_board[i][j] == 'v':
                    view_row.append(board[i][j])
                elif player_board[i][j] == 'h':
                    view_row.append(' ')
                else:
                    view_row.append(player_board[i][j])
            view.append(view_row)
        return view


class GameNewSerializer(serializers.Serializer):
    rows = serializers.IntegerField(min_value=3)
    columns = serializers.IntegerField(min_value=3)
    mines = serializers.IntegerField(min_value=1)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'games')