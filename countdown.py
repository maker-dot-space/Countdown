from __future__ import division
import time
import os
import configparser
import pygame
from threading import Timer
from pygame.locals import *

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

#os.path.join(data_dir, name)

config = configparser.ConfigParser()
config.read_file(open(os.path.join(data_dir, 'config.txt')))
FNAME_BACKGROUND = os.path.join(data_dir, config.get('options',
                                                   'fname_background'))
FNAME_ALARM = os.path.join(data_dir, config.get('options', 'fname_alarm'))
FNAME_AUDIO = os.path.join(data_dir, config.get('options', 'fname_audio'))
FNAME_FONT = os.path.join(data_dir, config.get('options', 'fname_font'))
BACK_COLOR = pygame.colordict.THECOLORS[config.get('options', 'back_color')]
TEXT_COLOR = pygame.colordict.THECOLORS[config.get('options', 'text_color')]
try:
    TEXT_BACK_COLOR = pygame.colordict.THECOLORS[config.get('options',
                                                            'text_back_color')]
except configparser.NoOptionError:
    TEXT_BACK_COLOR = None
TEXT_X = config.getint('options', 'text_x')
TEXT_Y = -config.getint('options', 'text_y')
SCREEN_FONT_RATIO = config.getint('options', 'screen_font_ratio')
ANIMATION_SPEED = config.getint('options', 'animation_speed')
ANIMATION_LENGHT = config.getfloat('options', 'animation_lenght')
DEFAULT_TIME = config.getint('options', 'default_time')

class CounterRender(object):
    def __init__(self, s):
        self.rect_to_clear = pygame.display.get_surface().get_rect()
        font_height = self.rect_to_clear.height // SCREEN_FONT_RATIO
        self.fnt = pygame.font.Font(FNAME_FONT, font_height)
        self.alarm_image = pygame.image.load(FNAME_ALARM).convert()
        self.alarm_image.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        screen_rect = pygame.display.get_surface().get_rect()

        # --------------------------------------------------------- #
        # Next Line Controls where the Counter will appear on screen
        self.screen_center = screen_rect.center #(100,100)
        # --------------------------------------------------------- #

        self.speed = ANIMATION_SPEED
        self.teta = 0

    def draw(self, surf):
        rects = self.rect_to_clear
        self.rect_to_clear = surf.blit(self.image, self.rect)
        return rects

    def clear(self, surf, background):
        surf.set_clip(self.rect_to_clear)
        surf.blit(background, (0, 0))
        surf.set_clip()

    def update(self, s):
        h = s // 3600
        # Seconds left.
        s = s % 3600
        m = s // 60
        s = s % 60
        # Convertion to string.
        h = str(h) if h > 9 else '0' + str(h)
        m = str(m) if m > 9 else '0' + str(m)
        s = str(s) if s > 9 else '0' + str(s)
        text = h + ':' + m + ':' + s
        
        # Next Line Controls Countdown Timer Color
        #TEXT_COLOR = (102,255,0)
        if TEXT_BACK_COLOR:
            self.image = self.fnt.render(text, True, TEXT_COLOR,
                                            TEXT_BACK_COLOR)
        else:
            self.image = self.fnt.render(text, True, TEXT_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (self.screen_center[0] + TEXT_X,
                            self.screen_center[1] + TEXT_Y)

class Counter(object):    
    def __init__(self, min_to_count):
        self.min_to_count = min_to_count
        self.sec_elapsed = int(0)
        self.s = 30

    def set_counter(self, min_to_count):
        self.min_to_count = min_to_count

    def start(self):
        self.start_time = time.time()

    def time_left(self):
        self.sec_elapsed = time.time() - self.start_time
        print(self.sec_elapsed)        
        return int(self.min_to_count * 60 - self.sec_elapsed)

    def update(self, state, dt):
        self.s = self.s - 1
        if state in ('idle', 'counting', 'resume'):
            if state == 'idle':
                self.s = self.min_to_count * 60
            elif state == 'resume':
                #self.start_time = time.time()
                #s = PAUSE_SECS
                #s = 10
                self.s = self.time_left()
                state = 'counting'
            elif state == 'counting':
                self.s = self.time_left()                

        elif state == 'ringing':
            # Conpute the position in degree.
            self.teta = self.teta + self.speed * dt / 1000.0
            if not (-3 < self.teta < 3):
                self.speed = -self.speed
            rotated_image = pygame.transform.rotate(self.alarm_image,
                                                    self.teta)
            self.image = rotated_image
            self.rect = self.image.get_rect()
            self.rect.center = self.screen_center


def main():

    # Initialize pygame.
    pygame.init()
    #pygame.display.set_mode((0, 0), FULLSCREEN)
    pygame.display.set_mode((800, 600))
    screen = pygame.display.get_surface()
    screen_rect = pygame.display.get_surface().get_rect()
    size = screen_rect.size
    # Hide the cursor.
    pygame.mouse.set_visible(False)
    # Initialize music.
    pygame.mixer.music.load(FNAME_AUDIO)
    # Draw a filled background.
    background = pygame.surface.Surface(size).convert()
    background.fill(BACK_COLOR)

    # Set the initial state.
    keep_running = True
    min_to_count = DEFAULT_TIME
    state = 'idle'
    counter = Counter(min_to_count)
    counterRender = CounterRender(158)

    clock = pygame.time.Clock()
    # Enter the main loop.
    while keep_running:
        # Pause.
        dt = clock.tick(25)
        # Parse user inputs.
        for event in pygame.event.get():
            if event.type == QUIT:
                keep_running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    keep_running = False
            elif state in ('idle', 'pause'):
                if event.type == KEYUP:
                    if event.key == K_RETURN:
                        if state == 'pause':                    
                            state = 'resume'
                        else:
                            counter.start()
                            state = 'counting'
                        
                    elif event.key == K_UP:
                        min_to_count += 1
                    elif event.key == K_DOWN:
                        min_to_count = max(0, min_to_count - 1)
                
                counter.set_counter(min_to_count)
            elif state == 'counting':
                if event.type == KEYUP:
                    if event.key == K_p:
                        state = 'pause'
                        
        # State machine.
        if state == 'counting':
            sec_left = counter.time_left()
            if sec_left <= 0:
                state = 'ringing'
                t_music_start = time.time()
                pygame.mixer.music.play()
        elif state == 'ringing':
            if not pygame.mixer.music.get_busy():
                # Exit if the sound alarm file ended
                keep_running = False
            elif ((time.time() - t_music_start) > ANIMATION_LENGHT):
                # Stop the sound alarm and quit after ANIMATION_LENGHT seconds.
                pygame.mixer.music.stop()
                keep_running = False

        counter.update(state, dt)
        counterRender.update(counter.s)
        counterRender.clear(screen, background)
        rects = counterRender.draw(screen)

        pygame.display.update(rects)

if __name__ == '__main__':
    main()
