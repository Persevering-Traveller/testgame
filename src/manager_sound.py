import pygame
import constants

class SoundManager():
    def __init__(self):
        self.mus_menu = None
        self.mus_level = None
        self.current_music = ""
        self.is_playing = False

        self.sfx_confirm = None
        self.sfx_gameover = None
        self.sfx_end = None
        self.sfx_hit = None
        self.sfx_jump = None
        self.sfx_hurt = None
    
    def load(self):
        # TODO Convert all .wav into .ogg
        self.mus_menu = "../assets/music/menu-theme.wav"
        self.mus_level = "../assets/music/level.wav"

        self.sfx_confirm = pygame.Sound("../assets/sfx/confirm-beep.wav")
        self.sfx_gameover = pygame.Sound("../assets/sfx/game-over.wav")
        self.sfx_end = pygame.Sound("../assets/sfx/end-of-level.wav")
        self.sfx_hit = pygame.Sound("../assets/sfx/hit.ogg")
        self.sfx_jump = pygame.Sound("../assets/sfx/jump.wav")
        self.sfx_hurt = pygame.Sound("../assets/sfx/player-died.wav")
    
    def play_sfx(self, sfx):
        match sfx:
            case constants.SOUNDFX.CONFIRM:
                self.sfx_confirm.play()
            case constants.SOUNDFX.GAMEOVER:
                self.sfx_gameover.play()
            case constants.SOUNDFX.END:
                self.sfx_end.play()
            case constants.SOUNDFX.HIT:
                self.sfx_hit.play()
            case constants.SOUNDFX.JUMP:
                self.sfx_jump.play()
            case constants.SOUNDFX.DIED:
                self.sfx_hurt.play()
    
    def play_music(self, music):
        if self.is_playing: return
        
        match music:
            case constants.MUSIC.MAIN_MENU:
                if self.current_music != self.mus_menu:
                    pygame.mixer.music.load(self.mus_menu)
                    pygame.mixer.music.play(-1)
                    self.current_music = self.mus_menu
                    self.is_playing = True
            case constants.MUSIC.LEVEL:
                if self.current_music != self.mus_level:
                    pygame.mixer.music.load(self.mus_level)
                    pygame.mixer.music.play(-1)
                    self.current_music = self.mus_level
                    self.is_playing = True
        
        if self.current_music != "":
            pygame.mixer.music.unpause()
    
    def stop_music(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.rewind()
        self.is_playing = False
        self.current_music = ""
    
    def pause_music(self):
        pygame.mixer.music.pause()
        self.is_playing = False