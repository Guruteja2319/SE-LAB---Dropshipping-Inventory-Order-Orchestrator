import io
import math
import struct
import wave

import pygame
from .player import Player
from .obstacle import Obstacle

# Game Engine

WHITE = (255, 255, 255)
BROWN = (120, 80, 40)
DARK_GREEN = (30, 100, 30)

class GameEngine:
    DIFFICULTIES = {
        "Easy": (4, 85),
        "Medium": (6, 70),
        "Hard": (8, 55),
    }
    DIFFICULTY_KEYS = {
        pygame.K_1: "Easy",
        pygame.K_2: "Medium",
        pygame.K_3: "Hard",
        pygame.K_4: "Exit",
    }

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ground_y = height - 40

        self.max_speed = 12
        self.speed_increase_per_frame = 0.003

        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_title_font = pygame.font.SysFont("Arial", 48)
        self.game_over_message_font = pygame.font.SysFont("Arial", 24)
        self.start_new_game("Medium")
        self._initialize_sounds()

    def start_new_game(self, difficulty):
        self.difficulty = difficulty
        self.speed, self.spawn_interval = self.DIFFICULTIES[difficulty]
        self.player = Player(80, self.ground_y)
        self._spawn_timer = 0
        self.obstacles = []
        self.distance = 0
        self.score = 0
        self.game_over = False
        self.quit_requested = False

    def _initialize_sounds(self):
        self.jump_sound = None
        self.score_sound = None
        self.game_over_sound = None

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            self.jump_sound = self._create_tone(660, 0.09, 0.2)
            self.score_sound = self._create_tone(880, 0.12, 0.2)
            self.game_over_sound = self._create_tone(220, 0.28, 0.2)
        except (pygame.error, OSError, ValueError, wave.Error):
            self.jump_sound = None
            self.score_sound = None
            self.game_over_sound = None

    @staticmethod
    def _create_tone(frequency, duration, volume):
        sample_rate = 22050
        frame_count = int(sample_rate * duration)
        frames = bytearray(frame_count * 2)
        for sample_index in range(frame_count):
            fade_in = min(1, sample_index / (sample_rate * 0.01))
            fade_out = min(1, (frame_count - sample_index) / (sample_rate * 0.03))
            envelope = min(fade_in, fade_out)
            sample = int(32767 * volume * envelope * math.sin(2 * math.pi * frequency * sample_index / sample_rate))
            struct.pack_into("<h", frames, sample_index * 2, sample)

        sound_data = io.BytesIO()
        with wave.open(sound_data, "wb") as sound_file:
            sound_file.setnchannels(1)
            sound_file.setsampwidth(2)
            sound_file.setframerate(sample_rate)
            sound_file.writeframes(frames)
        sound_data.seek(0)
        return pygame.mixer.Sound(file=sound_data)

    def _play_sound(self, sound):
        if sound is None:
            return

        try:
            sound.play()
        except pygame.error:
            self.jump_sound = None
            self.score_sound = None
            self.game_over_sound = None

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                selection = self.DIFFICULTY_KEYS.get(event.key)
                if selection == "Exit" or event.key == pygame.K_ESCAPE:
                    self.quit_requested = True
                elif selection is not None:
                    self.start_new_game(selection)
            return

        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            if self.player.on_ground:
                self.player.jump()
                self._play_sound(self.jump_sound)

    def handle_input(self):
        # Reserved for continuously-held-key input; this runner only
        # needs an edge-triggered jump, handled in handle_event.
        pass

    def update(self):
        if self.game_over:
            return

        self.speed = min(self.speed + self.speed_increase_per_frame, self.max_speed)
        previous_player_position = (self.player.x, self.player.y)
        self.player.update()

        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.obstacles.append(Obstacle(self.width, self.ground_y, self.speed))

        previous_obstacle_positions = [(obstacle.x, obstacle.y) for obstacle in self.obstacles]
        for obstacle in self.obstacles:
            obstacle.move()
            obstacle.speed = self.speed

        for obstacle, previous_obstacle_position in zip(self.obstacles, previous_obstacle_positions):
            if self._swept_collision(
                previous_player_position,
                previous_obstacle_position,
                self.player,
                obstacle,
            ):
                self.game_over = True
                self._play_sound(self.game_over_sound)
                return

        for obstacle in self.obstacles:
            if not obstacle.scored and obstacle.x + obstacle.width < self.player.x:
                obstacle.scored = True
                self.score += 1
                self._play_sound(self.score_sound)

        self.obstacles = [o for o in self.obstacles if not o.off_screen()]

        self.distance += self.speed

    @staticmethod
    def _swept_collision(previous_player_position, previous_obstacle_position, player, obstacle):
        relative_start_x = previous_obstacle_position[0] - previous_player_position[0]
        relative_start_y = previous_obstacle_position[1] - previous_player_position[1]
        relative_delta_x = (obstacle.x - previous_obstacle_position[0]) - (player.x - previous_player_position[0])
        relative_delta_y = (obstacle.y - previous_obstacle_position[1]) - (player.y - previous_player_position[1])

        def collision_times(relative_start, relative_delta, minimum, maximum):
            if relative_delta == 0:
                if minimum < relative_start < maximum:
                    return float("-inf"), float("inf")
                return None

            first = (minimum - relative_start) / relative_delta
            second = (maximum - relative_start) / relative_delta
            return min(first, second), max(first, second)

        x_times = collision_times(relative_start_x, relative_delta_x, -obstacle.width, player.width)
        y_times = collision_times(relative_start_y, relative_delta_y, -obstacle.height, player.height)
        if x_times is None or y_times is None:
            return False

        entry_time = max(x_times[0], y_times[0])
        exit_time = min(x_times[1], y_times[1])
        return entry_time <= exit_time and exit_time >= 0 and entry_time <= 1

    def render(self, screen):
        if self.game_over:
            screen.fill((24, 32, 38))
            title = self.game_over_title_font.render("GAME OVER", True, WHITE)
            final_score = self.game_over_message_font.render(f"Final Score: {self.score}", True, WHITE)

            screen.blit(title, title.get_rect(center=(self.width // 2, self.height // 2 - 55)))
            screen.blit(final_score, final_score.get_rect(center=(self.width // 2, self.height // 2 - 10)))

            options = (*self.DIFFICULTIES, "Exit")
            for index, option in enumerate(options, start=1):
                option_text = self.game_over_message_font.render(f"{index} - {option}", True, WHITE)
                screen.blit(option_text, option_text.get_rect(center=(self.width // 2, self.height // 2 + index * 35)))
            return

        pygame.draw.line(screen, BROWN, (0, self.ground_y), (self.width, self.ground_y), 4)

        pygame.draw.rect(screen, WHITE, self.player.rect())
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, DARK_GREEN, obstacle.rect())

        score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
