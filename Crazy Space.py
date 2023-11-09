import arcade
import random

#CONSTANTS
#Screen Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Crazy Space"

#Sprite Constants
CHARACTER_SCALING = 0.5

#Enemy Constants
ENEMY_COUNT = 2
ENEMY_SPEED = 1.5
WAVE_DELAY = 150

#Projectile Constants
BULLET_SPEED = 10
STAR_SPEED = 15 
STAR_COUNT = 5

#Powerups
# 1 to x Chance
CHANCE_OF_DROP = 8
CHANCE_OF_DROP_1 = 16
CHANCE_OF_DROP_2 = 8
POWER_UP_DURATION = 100
POWER_UP_DURATION_SPEED = 100

#Sound
SOUND_VOLUME = 0.5

#MAIN WINDOW
class CrazySpace(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        #GAME VARIABLES HERE

        #Sprite lists
        self.player_list = None
        self.enemy_list = None
        self.bullet_list = None
        self.power_up_list_acc_shooting = None
        self.power_up_list_kill_all = None
        self.power_up_list_speed = None
        
        self.list_of_enemy_sprites = []

        #Sprites
        self.player_sprite = None

        #Input Player
        self.move_left = False
        self.move_right = False
        self.on_power_up = False
        self.on_power_up_speed = False
        self.shot_delay = 0.4
        self.player_speed = 300
       
        #Score, Wave, state
        self.game_over = False
        self.score = 0
        self.wave = 0

        #Sounds
        self.hit_sound = arcade.load_sound("sounds/ENEMYHIT.wav")
        self.laser_sound = arcade.load_sound("sounds/LASERSHOT.wav")
        self.game_over_sound = arcade.load_sound("sounds/GAMEOVER.wav")
        self.power_up_sound = arcade.load_sound("sounds/POWERUP.wav")
        self.power_up_kill_all_sound = arcade.load_sound("sounds/KILLALL.wav")

        #Background
        self.backround = None
        arcade.set_background_color(arcade.color.AIR_FORCE_BLUE)


    def setup(self):
        #SET VARIABLE VALUES HERE

        #Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.power_up_list_acc_shooting = arcade.SpriteList()
        self.power_up_list_kill_all = arcade.SpriteList()
        self.power_up_list_speed = arcade.SpriteList()
        self.list_of_enemy_sprites = ["sprites/meteorGrey_big2.png","sprites/meteorGrey_big3.png","sprites/meteorGrey_big4.png"]

        #Sprites player
        self.player_sprite = arcade.Sprite("sprites/PlayerShip2_red.png", CHARACTER_SCALING)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = 20
        self.player_list.append(self.player_sprite)

        self.on_power_up = False
        self.on_power_up_speed = False

        #Track time
        self.time_since_wave_end = 0
        self.time_since_fired = 0
        self.time_since_power_up_picked = 0
        self.time_since_power_up_picked_speed = 0
        
        #Background
        self.background = arcade.load_texture("Backgrounds/giphy.gif")

    def on_draw(self):
        arcade.start_render()
        #RENDER OBJECTS ON SCREEN HERE
        #Background 
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        #Sprites
        self.enemy_list.draw()
        self.player_list.draw()
        self.bullet_list.draw()
        self.power_up_list_acc_shooting.draw()
        self.power_up_list_kill_all.draw()
        self.power_up_list_speed.draw()

        #Text
        score_gui = f"SCORE : {self.score}"
        wave_gui = f"WAVE : {self.wave}"
        final_score = f"FINAL SCORE : {self.score}"
        if self.game_over == False:
            arcade.draw_text(score_gui,5,5,arcade.color.WHITE,15, bold=True)
            arcade.draw_text(wave_gui,5,30,arcade.color.WHITE, 15, bold=True)

        #Game Over
        if self.game_over:
            arcade.draw_text("GAME OVER",210 , SCREEN_HEIGHT // 2, arcade.color.DIM_GRAY, 25, bold=True)
            arcade.draw_text(final_score,255 ,SCREEN_HEIGHT // 2 - 30, arcade.color.DIM_GRAY, 10, bold=True)

    #INPUT
    def on_key_press(self, key, modifiers):
        if key == arcade.key.RIGHT:
            self.move_right = True
        if key == arcade.key.LEFT:
            self.move_left = True
        if key == arcade.key.SPACE:
            if self.time_since_fired > self.shot_delay:
                bullet = arcade.Sprite("sprites/laserRed01.png", CHARACTER_SCALING)
                bullet.change_y = BULLET_SPEED
                bullet.center_x = self.player_sprite.center_x
                bullet.center_y = self.player_sprite.top
                arcade.play_sound(self.laser_sound, SOUND_VOLUME)
                self.bullet_list.append(bullet)
                self.time_since_fired = 0
            
    
    def on_key_release(self, key, modifiers):
        if key == arcade.key.RIGHT:
            self.move_right = False
        if key == arcade.key.LEFT:
            self.move_left = False


    def on_update(self, delta_time : float = 1 / 60):
        #UPDATE OBJECTS ON SCREEN HERE
        if self.game_over == False:
            self.bullet_list.update()
            self.player_list.update()
            self.enemy_list.update()
            self.power_up_list_acc_shooting.update()
            self.power_up_list_kill_all.update()
            self.power_up_list_speed.update()

            #Player movement
            if self.move_right and self.player_sprite.right < SCREEN_WIDTH:
                self.player_sprite.center_x += self.player_speed * delta_time
            if self.move_left and self.player_sprite.left > 0:
                self.player_sprite.center_x -= self.player_speed * delta_time

            if self.player_sprite.right > SCREEN_WIDTH:
                self.move_right = False
            if self.player_sprite.left < 0:
                self.move_left = False

            #BULLET
            #Track time since last shot
            if self.bullet_list != 0:
                self.time_since_fired += delta_time

            #Bullet Properties
            for bullet in self.bullet_list:
                hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

                if len(hit_list) > 0:
                    bullet.remove_from_sprite_lists()
            
                for enemy in hit_list:
                #Power up spawn on enemy death
                    if random.randint(1,CHANCE_OF_DROP) == 1:
                        power_up = arcade.Sprite("sprites/powerupBlue_bolt.png", CHARACTER_SCALING)
                        power_up.change_y = - ENEMY_SPEED * 2
                        power_up.center_x = enemy.center_x
                        power_up.center_y = enemy.bottom
                        self.power_up_list_acc_shooting.append(power_up)
                    
                    elif random.randint(1,CHANCE_OF_DROP_1) == 1:
                        power_up_1 = arcade.Sprite("sprites/powerupRed_bolt.png", CHARACTER_SCALING)
                        power_up_1.change_y = - ENEMY_SPEED * 2
                        power_up_1.center_x = enemy.center_x
                        power_up_1.center_y = enemy.bottom
                        self.power_up_list_kill_all.append(power_up_1)
                    
                    elif random.randint(1,CHANCE_OF_DROP_2) == 1:
                        power_up_speed = arcade.Sprite("sprites/bolt_gold.png", CHARACTER_SCALING)
                        power_up_speed.change_y = - ENEMY_SPEED * 2
                        power_up_speed.center_x = enemy.center_x
                        power_up_speed.center_y = enemy.bottom
                        self.power_up_list_speed.append(power_up_speed)

                    enemy.remove_from_sprite_lists()
                    arcade.play_sound(self.hit_sound, SOUND_VOLUME * 5)
                    self.score += 1 * self.wave
            
                    if bullet.bottom > SCREEN_HEIGHT:
                        bullet.remove_from_sprite_lists()
            
            #Power up 1 collision check - NEEDS FIXING
            for power_up in self.power_up_list_acc_shooting:
                if arcade.check_for_collision_with_list(self.player_sprite, self.power_up_list_acc_shooting):
                    self.time_since_power_up_picked = 0
                    self.on_power_up = True
                    arcade.play_sound(self.power_up_sound, SOUND_VOLUME)
                    power_up.remove_from_sprite_lists()
            #Power up 2 collision check and function
            for power_up_1 in self.power_up_list_kill_all:
                if arcade.check_for_collision_with_list(self.player_sprite, self.power_up_list_kill_all):
                    arcade.play_sound(self.power_up_sound, SOUND_VOLUME)
                    power_up_1.remove_from_sprite_lists()
                    for enemy in self.enemy_list:
                        self.score += 1 * self.wave
                        arcade.play_sound(self.power_up_kill_all_sound,SOUND_VOLUME)
                        enemy.remove_from_sprite_lists()
            #Power up 3 collision check
            for power_up_speed in self.power_up_list_speed:
                if arcade.check_for_collision_with_list(self.player_sprite, self.power_up_list_speed):
                    self.time_since_power_up_picked_speed = 0
                    self.on_power_up_speed = True
                    arcade.play_sound(self.power_up_sound, SOUND_VOLUME)
                    power_up_speed.remove_from_sprite_lists()

            #Power up 1 properties
            if self.on_power_up:
                self.shot_delay = 0
                self.time_since_power_up_picked += 1
                
            if self.time_since_power_up_picked > POWER_UP_DURATION:
                self.on_power_up = False
                self.shot_delay = 0.4

            for power_up in self.power_up_list_acc_shooting:
                if power_up.top < 0:
                    power_up.remove_from_sprite_lists()
            
            #Power up 2 properties
            for power_up_1 in self.power_up_list_kill_all:
                if power_up_1.top < 0:
                    power_up_1.remove_from_sprite_lists()
            
            #Power up 3 properties
            if self.on_power_up_speed:
                self.player_speed = 600
                self.time_since_power_up_picked_speed += 1
                
            if self.time_since_power_up_picked_speed > POWER_UP_DURATION_SPEED:
                self.on_power_up_speed = False
                self.player_speed = 300
                
            for power_up_speed in self.power_up_list_speed:
                if power_up_speed.top < 0:
                    power_up_speed.remove_from_sprite_lists()

            #ENEMY SPAWNER
            #Track time since last wave
            if self.wave == 0:
                self.time_since_wave_end = WAVE_DELAY + 1

            if len(self.enemy_list) == 0 and self.wave != 0:
                self.time_since_wave_end += 1

            #Spawns enemies
            if len(self.enemy_list) == 0 and self.time_since_wave_end > WAVE_DELAY:
                self.wave = self.wave + 1
                self.time_since_wave_end = 0
                for i in range (ENEMY_COUNT * self.wave):
                    enemy = arcade.Sprite(random.choice(self.list_of_enemy_sprites), CHARACTER_SCALING)
                    enemy.center_x = (random.randrange(20, SCREEN_WIDTH - 20))
                    enemy.center_y = (random.randrange(SCREEN_HEIGHT, SCREEN_HEIGHT + 400))
                    self.enemy_list.append(enemy)
        
            #Enemy movement
            for enemy in self.enemy_list:
                enemy.center_y -= ENEMY_SPEED
                if enemy.top < 0:
                    arcade.play_sound(self.game_over_sound, SOUND_VOLUME)
                    enemy.remove_from_sprite_lists()
                    self.game_over = True

        else:
            self.player_sprite.remove_from_sprite_lists()
            for enemy in self.enemy_list:
                enemy.remove_from_sprite_lists()
            for bullet in self.bullet_list:
                bullet.remove_from_sprite_lists()

#MAIN FUNCTION
def main():
    window = CrazySpace()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
