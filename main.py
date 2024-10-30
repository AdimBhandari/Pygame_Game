import pygame
import sys
import random

# Initialize Pygame
pygame.init()

#variables
width, height = 600, 400
ball_size = 20
paddle_width, paddle_height = 10, 60
fps = 60
white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)
blue = (0, 0, 128)

# paddle class
class paddle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((paddle_width, paddle_height))
        self.image.fill(white)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < height:
            self.rect.y += self.speed

# ball class
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((ball_size, ball_size))
        self.image.fill(red)
        self.rect = self.image.get_rect()
        self.reset_position()
        self.speed = 5

    def update(self):
        self.rect.x += self.speed * self.direction[0]
        self.rect.y += self.speed * self.direction[1]

        # Bounce off walls
        if self.rect.top <= 0 or self.rect.bottom >= height:
            self.direction[1] *= -1

    def reset_position(self):
        self.rect.center = (width // 2, height // 2)
        self.direction = [random.choice([-1, 1]), random.choice([-1, 1])]

# a paddle class
class AIpaddle(paddle):
    def update(self, ball):  
        # Add random mistakes to the AI
        if random.random() < 0.1:  # 10% chance to miss
            return
        
        if ball.rect.centery > self.rect.centery and self.rect.bottom < height:
            self.rect.y += self.speed
        if ball.rect.centery < self.rect.centery and self.rect.top > 0:
            self.rect.y -= self.speed

# menu class
class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 74)
        self.title = "Pong"
        self.instruction = "Press ENTER to Start"
        
    def draw(self):
        self.screen.fill(blue)
        
        title_text = self.font.render(self.title, True, white)
        title_rect = title_text.get_rect(center=(width // 2, height // 2 - 40))
        self.screen.blit(title_text, title_rect)
        
        instruction_text = self.font.render(self.instruction, True, white)
        instruction_rect = instruction_text.get_rect(center=(width // 2, height // 2 + 40))
        self.screen.blit(instruction_text, instruction_rect)

# scoreboard class
class Scoreboard:
    def __init__(self):
        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen):
        score_text = f"Player: {self.player_score}  AI: {self.ai_score}"
        score_surface = self.font.render(score_text, True, white)
        screen.blit(score_surface, (width // 2 - score_surface.get_width() // 2, 10))

    def reset(self):
        self.player_score = 0
        self.ai_score = 0

# intro screen class
class IntroScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.instructions = [
            "Controls:",
            "UP Arrow - Move Up",
            "DOWN Arrow - Move Down",
            "P - Pause",
            "ESC - Quit to Menu"
        ]
        self.countdown = 7

    def draw(self):
        self.screen.fill(blue)
        for i, line in enumerate(self.instructions):
            text_surface = self.font.render(line, True, white)
            self.screen.blit(text_surface, (width // 2 - text_surface.get_width() // 2, height // 2 - 60 + i * 30))

        countdown_text = self.font.render(f"Countdown: {self.countdown}", True, white)
        self.screen.blit(countdown_text, (width // 2 - countdown_text.get_width() // 2, 10))

# main function
def main():
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("1 Player Pong")

    # initialize menu, scoreboard, intro screen, and game variables
    menu = Menu(screen)
    scoreboard = Scoreboard()
    intro = IntroScreen(screen)

    # create paddles and ball
    player = paddle(20, height // 2)
    ai = AIpaddle(width - 20, height // 2)
    ball = Ball()

    all_sprites = pygame.sprite.Group(player, ai, ball)

    running = True
    game_active = False
    paused = False
    show_intro = False 

    while running:
        if show_intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            intro.draw()
            pygame.display.flip()

            # countdown logic
            if intro.countdown > 0:
                pygame.time.delay(1000)  # wait 1 second
                intro.countdown -= 1
            else:
                show_intro = False  # start the game after countdown
                game_active = True   # activate the game after intro

        elif not game_active:
            # display menu
            menu.draw()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        show_intro = True  # show the intro screen
                        intro.countdown = 7  # reset countdown
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # return to menu
                        game_active = False
                    if event.key == pygame.K_p:  # pause the game
                        paused = not paused

            if not paused:
                # update player paddle and ball
                player.update()  # Update player paddle
                ai.update(ball)  # Update AI paddle with ball reference
                ball.update()  # Update ball position

                # check for collisions with paddles
                if pygame.sprite.spritecollide(ball, [player, ai], False):
                    ball.direction[0] *= -1

                # update score if the ball goes out of bounds
                if ball.rect.left <= 0:  # AI scores
                    scoreboard.ai_score += 1
                    ball.reset_position()
                elif ball.rect.right >= width:  # Player scores
                    scoreboard.player_score += 1
                    ball.reset_position()

                # draw everything
                screen.fill(black)
                all_sprites.draw(screen)
                scoreboard.draw(screen)
                pygame.display.flip()

        clock.tick(fps)

if __name__ == "__main__":
    main()
