from enum import Enum
import pygame
import constants
from actor import Actor

class PLAYERSTATES(Enum):
    IDLE = 0
    MOVING = 1
    JUMPING = 2
    HURT = 3
    DIED = 4
    WIN = 5
    PAUSED = 6

MAX_X_VELOCITY = 2.0
MAX_Y_VELOCITY = 2.0 # TODO play with and change these values (the velocity)
SUB_STEP_VELOCITY = 4

class Player(Actor):
    def __init__(self) -> None:
        super().__init__()

        self.health = 3

        self.jump_force = -4.0
        self.pushback_force_x = self.pushback_force_x * 1.2 # Fling back a little farther than normal

        self.current_state = PLAYERSTATES.IDLE

        self.enemy_ref = None # TODO Get list of awake enemies from Enemy Manager when created

        self.hurt_timer = None
        self.start_over_timer = None

    def load(self):
        self.sprite = pygame.image.load("../assets/sprites/player-sheet.png").convert_alpha()
        self.pos_rect = pygame.Rect(80, 80, self.collision_dimensions[0], self.collision_dimensions[1])
        self.world_pos = self.pos_rect.copy() # Initially, pos_rect of screen space is the same as world pos
        self.initial_world_pos = self.world_pos.copy()

        self.anim_frames.append(pygame.Rect(0, 0, self.sprite_frame_size, self.sprite_frame_size)) # Idle
        for i in range(3):
            self.anim_frames.append(pygame.Rect(self.sprite_frame_size * i, self.sprite_frame_size, self.sprite_frame_size, self.sprite_frame_size)) # Moving
        self.anim_frames.append(pygame.Rect(0, self.sprite_frame_size * 2, self.sprite_frame_size, self.sprite_frame_size)) # Jumping
        self.anim_frames.append(pygame.Rect(0, self.sprite_frame_size * 3, self.sprite_frame_size, self.sprite_frame_size)) # Hurt and Dying
        
        self.hurt_timer = constants.TIMER_MANAGER.new_timer(1)
        self.start_over_timer = constants.TIMER_MANAGER.new_timer(2)

    def update(self, dt):
        self.anim_counter += dt # Needed here for animation

        last_dir = self.direction
        
        pressed_keys = pygame.key.get_pressed()
        #just_p_keys = pygame.key.get_just_pressed()

        match self.current_state:
            case PLAYERSTATES.IDLE:
                self.move_left_right(pressed_keys)
                self.jump(pressed_keys)
            case PLAYERSTATES.MOVING:
                self.move_left_right(pressed_keys)
                self.jump(pressed_keys)
                last_dir = self.deaccelerate_left_right(pressed_keys, dt)
            case PLAYERSTATES.JUMPING:
                self.move_left_right(pressed_keys)
                last_dir = self.deaccelerate_jumping(pressed_keys, dt)
            case PLAYERSTATES.HURT | PLAYERSTATES.DIED:
                pass


        self.y_velocity += self.gravity * dt
        if self.current_state != PLAYERSTATES.HURT and self.current_state != PLAYERSTATES.DIED:
            self.x_velocity += self.direction * self.acceleration * dt
        elif self.current_state == PLAYERSTATES.HURT:
            if self.is_grounded:
                self.x_velocity = 0

        # For flipping the sprite if we're facing in another direction
        if last_dir != self.direction:
            if self.direction < 0: self.facing = -1
            else: self.facing = 1

        # Cap velocity only when not hurt or dead
        if (abs(self.x_velocity) >= MAX_X_VELOCITY and 
            self.current_state != PLAYERSTATES.HURT and 
            self.current_state != PLAYERSTATES.DIED):
            self.x_velocity = MAX_X_VELOCITY * self.direction
        
        if self.current_state != PLAYERSTATES.DIED:
            self.x_collision_check(self.x_velocity)
            self.y_collision_check(self.y_velocity)
        else:
            self.pos_rect.move_ip(self.x_velocity, self.y_velocity) # Fly off screen if dead

        # TODO Check for overlapping only on awake enemies
        overlapping_side = self.get_overlapping_side(self.enemy_ref)
        if (overlapping_side != None and 
            self.current_state != PLAYERSTATES.HURT and 
            self.current_state != PLAYERSTATES.DIED):
            # Player can be hurt from left, right, and top sides, but not bottom
            if overlapping_side != constants.COLLISIONSIDE.BOTTOM: 
                self.health -= 1
                match overlapping_side:
                    case constants.COLLISIONSIDE.LEFT:
                        self.x_velocity = self.pushback_force_x
                    case constants.COLLISIONSIDE.RIGHT:
                        self.x_velocity = -self.pushback_force_x
                    case constants.COLLISIONSIDE.TOP:
                        # TODO This needs testing
                        if self.pos_rect.center > self.enemy_ref.pos_rect.center:
                            self.x_velocity = self.pushback_force_x
                        else:
                            self.x_velocity = -self.pushback_force_x
                self.y_velocity = self.pushback_force_y
                self.awake = False
                pygame.event.post(pygame.Event(constants.CUSTOMEVENTS.PLAYER_HURT))
                if self.health > 0:
                    constants.TIMER_MANAGER.start_timer(self.hurt_timer)
                    self.current_state = PLAYERSTATES.HURT
                elif self.health <= 0:
                    constants.TIMER_MANAGER.start_timer(self.start_over_timer)
                    self.current_state = PLAYERSTATES.DIED
            else: # Bounce off enemies like jumping
                self.y_velocity = self.jump_force
                self.current_state = PLAYERSTATES.JUMPING
            # Player is flung up into the air regardless of how the overlap happened
            self.is_grounded = False
        
        for event in pygame.event.get(constants.CUSTOMEVENTS.TIMER_ENDED):
            if event.type == constants.CUSTOMEVENTS.TIMER_ENDED:
                if event.dict["id"] == self.hurt_timer:
                   self.awake = True
                   self.direction = 0 # Needs to be set to zero or the player will float towards the last running direction
                   self.current_state = PLAYERSTATES.IDLE
                elif event.dict["id"] == self.start_over_timer:
                    pygame.event.post(pygame.Event(constants.CUSTOMEVENTS.PLAYER_DIED))


        # Screen Boundaries
        if self.pos_rect.x < 0:
            self.pos_rect.x = 0
        elif self.pos_rect.x + self.pos_rect.width > constants.CANVAS_WIDTH: 
            self.pos_rect.x = constants.CANVAS_WIDTH - self.pos_rect.width
        # World Boundaries
        if self.world_pos.x < 0: 
            self.world_pos.x = 0
        elif self.world_pos.x + self.world_pos.width > constants.TILE_SIZE * constants.LEVEL_TILE_WIDTH: 
            self.world_pos.x = constants.TILE_SIZE * constants.LEVEL_TILE_WIDTH - self.world_pos.width

        if self.pos_rect.y < -32: self.pos_rect.y = -32
        elif self.pos_rect.y + self.pos_rect.height > 144: # if player falls in a pit
            self.health = 0
            pygame.event.post(pygame.Event(constants.CUSTOMEVENTS.PLAYER_HURT))
            constants.TIMER_MANAGER.start_timer(self.start_over_timer)
            self.current_state = PLAYERSTATES.DIED


    def draw(self, canvas: pygame.Surface):
        match self.current_state:
            case PLAYERSTATES.IDLE:
                self.anim_index = 0
            case PLAYERSTATES.MOVING:
                if self.anim_counter >= self.anim_speed:
                    self.anim_index += 1
                    self.anim_counter = 0.0
                    
                if self.anim_index < 1 or self.anim_index > 3: self.anim_index = 1 # The Starting frame for Moving animation
            case PLAYERSTATES.JUMPING:
                self.anim_index = 4
            case PLAYERSTATES.HURT | PLAYERSTATES.DIED:
                self.anim_index = 5
        
        # Actual blit code held in the Actor class's draw
        super().draw(canvas)
        # DEBUG
        #pygame.draw.rect(canvas, "red", self.pos_rect, 1)

    def move_left_right(self, pressed_keys):
        if pressed_keys[pygame.K_a]:
            if self.is_grounded and self.current_state != PLAYERSTATES.JUMPING:
                self.current_state = PLAYERSTATES.MOVING
            self.direction = -1
        if pressed_keys[pygame.K_d]:
            if self.is_grounded and self.current_state != PLAYERSTATES.JUMPING:
                self.current_state = PLAYERSTATES.MOVING
            self.direction = 1

    def jump(self, just_pressed_keys):
        if just_pressed_keys[pygame.K_j]:
                self.current_state = PLAYERSTATES.JUMPING
                self.is_grounded = False
                self.y_velocity = self.jump_force
    
    def deaccelerate_left_right(self, pressed_keys, dt):
        if not pressed_keys[pygame.K_a] and not pressed_keys[pygame.K_d]:
            # Don't change state back to idle until the player has reached 0 X velocity on the ground (or close to)
            if self.is_grounded:
                if abs(self.x_velocity) < 0.25: # TODO Play with this value some more
                    self.current_state = PLAYERSTATES.IDLE
                else:
                    self.current_state = PLAYERSTATES.MOVING
            self.direction = 0
            last_dir = self.direction
            if self.x_velocity != 0:
                if self.x_velocity < 0:
                    self.x_velocity += self.deacceleration * dt
                else:
                    self.x_velocity -= self.deacceleration * dt
            # Needed or the player will stop and face right when running on ground
            return last_dir
    
    def deaccelerate_jumping(self, pressed_keys, dt):
        # Needs to be out of the not pressing left or right keys check or else we won't change state if still moving
        if self.is_grounded:
            if abs(self.x_velocity) < 0.25: # TODO Play with this value some more
                self.current_state = PLAYERSTATES.IDLE
            else:
                self.current_state = PLAYERSTATES.MOVING

        if not pressed_keys[pygame.K_a] and not pressed_keys[pygame.K_d]:
            self.direction = 0
            last_dir = self.direction
            if self.x_velocity != 0:
                if self.x_velocity < 0:
                    self.x_velocity += self.deacceleration * dt
                else:
                    self.x_velocity -= self.deacceleration * dt
            return last_dir
                
    def reset(self):
        super().reset()
        self.health = 3
        self.current_state = PLAYERSTATES.IDLE
        self.pos_rect.x = 80
        self.pos_rect.y = 80