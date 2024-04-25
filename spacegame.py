import pygame, sys, os, random, math
from pygame.locals import *

# sounds
pygame.mixer.pre_init()
pygame.init()

fps = pygame.time.Clock()

# colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# globals
WIDTH = 800
HEIGHT = 600
time_elapsed = 0

# canvas declaration
window_surface = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption('Space Shooter')

# load images
background_img = pygame.image.load(os.path.join('images', 'bg.jpg'))
debris_img = pygame.image.load(os.path.join('images', 'debris2_brown.png'))
player_img = pygame.image.load(os.path.join('images', 'ship.png'))
player_thruster_img = pygame.image.load(os.path.join('images', 'ship_thrusted.png'))
enemy_img = pygame.image.load(os.path.join('images', 'asteroid.png'))
bullet_img = pygame.image.load(os.path.join('images', 'shot2.png'))
explosion_img = pygame.image.load(os.path.join('images', 'explosion_blue.png'))

# load sounds
missile_sound_effect = pygame.mixer.Sound(os.path.join('sounds', 'missile.ogg'))
missile_sound_effect.set_volume(1)

thruster_sound_effect = pygame.mixer.Sound(os.path.join('sounds', 'thrust.ogg'))
thruster_sound_effect.set_volume(1)

explosion_sound_effect = pygame.mixer.Sound(os.path.join('sounds', 'explosion.ogg'))
explosion_sound_effect.set_volume(1)

# background music
pygame.mixer.music.load(os.path.join('sounds', 'game.ogg'))
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play()

# set variables
player_x = WIDTH / 2 - 50
player_y = HEIGHT / 2 - 50
player_angle = 0
player_is_rotating = False
player_is_accelerating = False
player_rotation_direction = 0
player_speed = 0

enemy_x_positions = [0, 0, 0, 0, 0]  # random.randint(0,WIDTH)
enemy_y_positions = [0, 0, 0, 0, 0]  # random.randint(0,HEIGHT)
enemy_angles = []
enemy_speed = 2
num_enemies = 5

bullet_x_positions = []
bullet_y_positions = []
bullet_angles = []
num_bullets = 0

score = 0
game_over = False

for i in range(0, num_enemies):
    enemy_x_positions.append(random.randint(0, WIDTH))
    enemy_y_positions.append(random.randint(0, HEIGHT))
    enemy_angles.append(random.randint(0, 365))


def rotate_image(image, angle):
    """Rotate a surface while keeping its center."""

    original_rect = image.get_rect()
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_rect = original_rect.copy()
    rotated_rect.center = rotated_image.get_rect().center
    rotated_image = rotated_image.subsurface(rotated_rect).copy()
    return rotated_image


# draw game function
def draw_game(canvas):
    global time_elapsed
    global player_is_accelerating
    global bullet_x_positions, bullet_y_positions
    global score

    canvas.fill(BLACK)
    canvas.blit(background_img, (0, 0))
    canvas.blit(debris_img, (time_elapsed * .3, 0))
    canvas.blit(debris_img, (time_elapsed * .3 - WIDTH, 0))
    time_elapsed += 1

    for i in range(0, num_bullets):
        canvas.blit(bullet_img, (bullet_x_positions[i], bullet_y_positions[i]))

    for i in range(0, num_enemies):
        canvas.blit(rotate_image(enemy_img, time_elapsed), (enemy_x_positions[i], enemy_y_positions[i]))

    if player_is_accelerating:
        canvas.blit(rotate_image(player_thruster_img, player_angle), (player_x, player_y))
    else:
        canvas.blit(rotate_image(player_img, player_angle), (player_x, player_y))

    # draw Score
    score_font = pygame.font.SysFont("Comic Sans MS", 40)
    score_label = score_font.render("Score : " + str(score), 1, (255, 255, 0))
    canvas.blit(score_label, (50, 20))

    if game_over:
        game_over_font = pygame.font.SysFont("Comic Sans MS", 80)
        game_over_label = game_over_font.render("GAME OVER ", 1, (255, 255, 255))
        canvas.blit(game_over_label, (WIDTH / 2 - 150, HEIGHT / 2 - 40))


# handle input function
def handle_input_events():
    global player_angle, player_is_rotating, player_rotation_direction
    global player_x, player_y, player_speed, player_is_accelerating
    global bullet_x_positions, bullet_y_positions, bullet_angles, num_bullets
    global thruster_sound_effect, missile_sound_effect

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_RIGHT:
                player_is_rotating = True
                player_rotation_direction = 0
            elif event.key == K_LEFT:
                player_is_rotating = True
                player_rotation_direction = 1
            elif event.key == K_UP:
                player_is_accelerating = True
                player_speed = 10
                thruster_sound_effect.play()
            elif event.key == K_SPACE:
                bullet_x_positions.append(player_x + 50)
                bullet_y_positions.append(player_y + 50)
                bullet_angles.append(player_angle)
                num_bullets += 1
                missile_sound_effect.play()

        elif event.type == KEYUP:
            if event.key == K_LEFT or event.key == K_RIGHT:
                player_is_rotating = False
            else:
                player_is_accelerating = False
                thruster_sound_effect.stop()

    if player_is_rotating:
        if player_rotation_direction == 0:
            player_angle -= 10
        else:
            player_angle += 10

    if player_is_accelerating or player_speed > 0:
        player_x += math.cos(math.radians(player_angle)) * player_speed
        player_y += -math.sin(math.radians(player_angle)) * player_speed
        if not player_is_accelerating:
            player_speed -= 0.2


# update the screen
def update_screen():
    pygame.display.update()
    fps.tick(60)


def is_collision_detected(enemy_x, enemy_y, bullet_x, bullet_y, distance_threshold):
    distance = math.sqrt(math.pow(enemy_x - bullet_x, 2) + (math.pow(enemy_y - bullet_y, 2)))
    if distance < distance_threshold:
        return True
    else:
        return False


def process_game_logic():
    global bullet_x_positions, bullet_y_positions, bullet_angles, num_bullets
    global enemy_x_positions, enemy_y_positions
    global score
    global game_over

    for i in range(0, num_bullets):
        bullet_x_positions[i] += math.cos(math.radians(bullet_angles[i])) * 10
        bullet_y_positions[i] += -math.sin(math.radians(bullet_angles[i])) * 10

    for i in range(0, num_enemies):
        enemy_x_positions[i] += math.cos(math.radians(enemy_angles[i])) * enemy_speed
        enemy_y_positions[i] += -math.sin(math.radians(enemy_angles[i])) * enemy_speed

        if enemy_y_positions[i] < 0:
            enemy_y_positions[i] = HEIGHT

        if enemy_y_positions[i] > HEIGHT:
            enemy_y_positions[i] = 0

        if enemy_x_positions[i] < 0:
            enemy_x_positions[i] = WIDTH

        if enemy_x_positions[i] > WIDTH:
            enemy_x_positions[i] = 0

        if is_collision_detected(player_x, player_y, enemy_x_positions[i], enemy_y_positions[i], 27):
            game_over = True

    for i in range(0, num_bullets):
        for j in range(0, num_enemies):
            if is_collision_detected(bullet_x_positions[i], bullet_y_positions[i], enemy_x_positions[j],
                                     enemy_y_positions[j], 50):
                enemy_x_positions[j] = (random.randint(0, WIDTH))
                enemy_y_positions[j] = (random.randint(0, HEIGHT))
                enemy_angles[j] = (random.randint(0, 365))
                explosion_sound_effect.play()
                score += 1


# asteroids game loop
while True:
    draw_game(window_surface)
    handle_input_events()
    if not game_over:
        process_game_logic()
    update_screen()
