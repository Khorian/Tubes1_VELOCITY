# ini kode bot program
import random
from game.logic.base import BaseLogic
from game.models import Board, GameObject, Position
from game.util import get_direction

class VelocityBot(BaseLogic):
    def __init__(self):
        self.goal_position = None
        self.returning_to_base = False

    def next_move(self, board_bot: GameObject, board: Board):
        bot_pos = board_bot.position
        inventory = board_bot.properties.diamonds or 0
        inventory_limit = board_bot.properties.inventory_size or 5
        base_pos = board_bot.properties.base

        # Cek jika sedang kembali ke base
        if self.returning_to_base:
            if bot_pos == base_pos:
                # Setor diamond dan reset status
                board_bot.properties.diamonds = 0
                self.returning_to_base = False
                self.goal_position = self.get_best_diamond_position(bot_pos, board)
                if self.goal_position == bot_pos:
                    self.goal_position = None
                    return self.random_valid_move(bot_pos, board)
                return self.move_towards_goal(bot_pos, board, board_bot)
            else:
                self.goal_position = base_pos
                return self.move_towards_goal(bot_pos, board, board_bot)

        # Inventory penuh, kembali ke base
        if inventory >= inventory_limit:
            self.returning_to_base = True
            self.goal_position = base_pos
            return self.move_towards_goal(bot_pos, board, board_bot)

        # Cek jika di posisi diamond
        self.goal_position = self.get_best_diamond_position(bot_pos, board)
        if self.goal_position == bot_pos:
            return self.random_valid_move(bot_pos, board)

        # Gerak ke arah diamond
        return self.move_towards_goal(bot_pos, board, board_bot)

    def move_towards_goal(self, bot_pos: Position, board: Board, board_bot: GameObject):
        if self.goal_position and self.goal_position != bot_pos:
            dx, dy = get_direction(bot_pos.x, bot_pos.y, self.goal_position.x, self.goal_position.y)
            new_x = bot_pos.x + dx
            new_y = bot_pos.y + dy

            if self.is_valid_move(new_x, new_y, board,
                                  allow_base=True,
                                  bot_base=board_bot.properties.base):
                return dx, dy

        return self.random_valid_move(bot_pos, board)

    def get_best_diamond_position(self, bot_pos: Position, board: Board):
        best_target = None
        best_score = -1
        best_distance = float('inf')

        for obj in board.diamonds:
            score = obj.properties.score or 1
            dist = abs(obj.position.x - bot_pos.x) + abs(obj.position.y - bot_pos.y)

            if score > best_score or (score == best_score and dist < best_distance):
                best_target = obj
                best_score = score
                best_distance = dist

        return best_target.position if best_target else None

    def is_valid_move(self, x, y, board: Board, allow_base=False, bot_base=None):
        if not (0 <= x < board.width and 0 <= y < board.height):
            return False

        for obj in board.game_objects:
            if obj.position.x == x and obj.position.y == y:
                if obj.type not in ["DiamondGameObject", "TeleportGameObject", "RedButtonGameObject"]:
                    if allow_base and bot_base and (x, y) == (bot_base.x, bot_base.y):
                        return True
                    return False
        return True

    def random_valid_move(self, pos: Position, board: Board):
        moves = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        random.shuffle(moves)
        for dx, dy in moves:
            new_x = pos.x + dx
            new_y = pos.y + dy
            if self.is_valid_move(new_x, new_y, board):
                return dx, dy
        return 0, 0
      
