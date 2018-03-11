# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import random
from django.db import models


class Game(models.Model):
    """Represents a game started by a user"""

    STATE_NEW = 0
    STATE_STARTED = 1
    STATE_PAUSED = 2
    STATE_TIMEOUT = 3
    STATE_WON = 4
    STATE_LOST = 5
    STATE_CHOICES = (
        (STATE_NEW, 'new'),
        (STATE_STARTED, 'started'),
        (STATE_PAUSED, 'paused'),
        (STATE_TIMEOUT, 'timeout'),
        (STATE_WON, 'won'),
        (STATE_LOST, 'lost'),
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255, blank=True, default='Game')

    board = models.TextField(blank=True, default='', help_text='Board as a JSON matrix. (0-9: adjacent mines, x: mine)')
    player_board = models.TextField(blank=True, default='',
                                    help_text='Board as a JSON matrix. (v: visible, h: hidden, ?: question mark, !: exclamation mark.')
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_NEW)
    duration_seconds = models.IntegerField(default=90,  help_text='Game duration: 90 seconds')
    player = models.ForeignKey('auth.User', related_name='games', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'
        ordering = ('created',)

    def __str__(self):
        return self.title

    @staticmethod
    def _inside_board(rows, cols, point):
        """ Returns whether the point is inside the board (specified by rows,cols) or not (overflow)"""
        y, x = point
        return (0 <= x < cols) and (0 <= y < rows)

    @staticmethod
    def _adjacent_points(rows, cols, x, y):
        """Given a point(x,y) in the board (specified by rows,cols) this returns all adjacent points"""
        up = (y - 1, x)
        down = (y + 1, x)
        left = (y, x - 1)
        right = (y, x + 1)
        upper_right = (y - 1, x + 1)
        upper_left = (y - 1, x - 1)
        lower_right = (y + 1, x + 1)
        lower_left = (y + 1, x - 1)
        points = [up, down, left, right, upper_left, upper_right, lower_left, lower_right]
        return [p for p in points if Game._inside_board(rows, cols, p)]

    @staticmethod
    def _fill_adjacent(board, rows, cols, x, y):
        """If the point has a mine (x) this updates all adjacent points with current value + 1"""
        if board[y][x] == 'x':
            for p in Game._adjacent_points(rows, cols, x, y):
                py, px = p
                if board[py][px] != 'x':
                    board[py][px] = str(int(board[py][px]) + 1)

    @staticmethod
    def new_boards(rows, cols, mines):
        """Creates and returns a new boards and a new player_board"""
        assert mines < (rows * cols)  # to make sure that there are fewer mines than fields

        board = [['0' for j in range(cols)] for i in range(rows)]
        player_board = [['h' for j in range(cols)] for i in range(rows)]
        for i in range(mines):
            mine_set = False
            while not mine_set:
                x = random.randint(0, cols - 1)
                y = random.randint(0, rows - 1)
                if board[y][x] != 'x':
                    board[y][x] = 'x'
                    mine_set = True  # distributes mines randomly in the board
        for i in range(rows):
            for j in range(cols):
                Game._fill_adjacent(board, rows, cols, j, i)  # for each field with a mine it updates adj fields' values
        return json.dumps(board), json.dumps(player_board)

    def reveal_at(self, x, y):
        """
        Reveals a field in point (x,y)
        If if is already revealed ('v') exits the function.
        Else it marks the field as revealed. Also if the field has not adjacent fields with mines in them, it calls the
        function recursively in order to reveal all the adj fields until a field with value > 0 is found.
        """
        pboard = json.loads(self.player_board)
        if pboard[y][x] != 'v':
            pboard[y][x] = 'v'
            self.player_board = json.dumps(pboard)
            board = json.loads(self.board)
            rows, cols = len(board), len(board[0])
            if board[y][x] == '0':
                for p in Game._adjacent_points(rows, cols, x, y):
                    py, px = p
                    self.reveal_at(px, py)

    def is_mine_at(self, x, y):
        """Returns whether the field has a mine in it or not"""
        board = json.loads(self.board)
        return board[y][x] == 'x'

    def is_all_revealed(self):
        """Returns whether the board is all revealed (except for the fields with a mine in it) or not"""
        board = json.loads(self.board)
        pboard = json.loads(self.player_board)
        rows, cols = len(board), len(board[0])
        for i in range(rows):
            for j in range(cols):
                if board[i][j] != 'x' and pboard[i][j] != 'v':
                    return False
        return True

    def mark_flag_at(self, x, y):
        """Marks a field with a flag"""
        board = json.loads(self.player_board)
        board[y][x] = '!'
        self.player_board = json.dumps(board)

    def mark_question_at(self, x, y):
        """Marks a field with a question mark"""
        board = json.loads(self.player_board)
        board[y][x] = '?'
        self.player_board = json.dumps(board)
