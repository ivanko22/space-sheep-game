# implementation of Spaceship - program template for RiceRocks
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
time_a = 0
started = False
rock_group = set([])
missile_group = set([])
explosion_group = set([])
num_rock = 0

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
# .ogg versions of sounds are also available, just replace .mp3 by .ogg
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
soundtrack.set_volume(.5)
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

print num_rock

# Ship class
class Ship:

    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0], self.image_center[1]] , self.image_size,
                              self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)
        # canvas.draw_circle(self.pos, self.radius, 1, "White", "White")

    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        # update velocity
        if self.thrust:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * .1
            self.vel[1] += acc[1] * .1
            
        self.vel[0] *= .99
        self.vel[1] *= .99

    def set_thrust(self, on):
        self.thrust = on
        if on:
            ship_thrust_sound.rewind()
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.pause()
       
    def increment_angle_vel(self):
        self.angle_vel += .05
        
    def decrement_angle_vel(self):
        self.angle_vel -= .05
        
    def shoot(self):
        global a_missile
        forward = angle_to_vector(self.angle)
        
        missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
        missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
        
        #a_missile = Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound)
        missile = Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound)

        missile_group.add(missile)
    
# Sprite class
class Sprite:
    global distance, rock_group, score, missile_group

    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        global time_a, explosion_info, explosion_group, current_rock_index
      
        if self.animated == True:
            current_rock_index = (time_a % explosion_info.lifespan) // 1
            current_rock_center = [explosion_info.center[0] +  current_rock_index * explosion_info.size[0], explosion_info.center[1]]
            canvas.draw_image(explosion_image, current_rock_center, explosion_info.size, self.pos, explosion_info.size)    		
            time_a += 0.2    
            
            if time_a >= 23:
                for exp in explosion_group:
                    remove_exp = set([])
                    remove_exp.add(exp)
                    explosion_group.difference_update(remove_exp)
                    time_a = 0
  
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)
            

    def update(self):
        global explosion_group
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        self.lifespan = True
        
    def get_position(self):
        return self.pos

    def distance(point1, point2):
        #global distance
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
        print point1, point2
        
        
    def collide(self, other_sprites):
        global lives, rock_group, score, missile_group
        self.other_sprites = other_sprites

        d_sprite = other_sprites.pos
        d_sprite_radius = other_sprites.radius
        d_ship = my_ship.pos
        d_ship_radius = my_ship.radius
        d = distance(d_sprite, d_ship)
    
        if d < (d_sprite_radius + d_ship_radius):
            remove = set([])
            other_sprites.animated = True
            explosion_sound.rewind()
            explosion_sound.play()
            remove.add(other_sprites)
            explosion_group.add(other_sprites)
            rock_group.difference_update(remove)
            lives -= 1
            score += 100
   

# Two objects collide if the distance between their
#	centers is less than the sum of their radii.
#	def collide(center1, center2, radius1, radius2):
#    	if distance(center1, center2) < (radius1 + radius2):
#        	return True
#    	else:
#        	return False   
#    
 
def group_collide(rocks, missile):
    global lives, rock_group, score, missile_group, started, click, explosion_group
        
    for rock in rocks:
        d_rock = rock.pos
        d_rock_radius = rock.radius
        
        for miss in missile:
            d_missile = miss.pos
            d_missile_radius = miss.radius
            d = distance(d_rock, d_missile)
            #print d
        
            if d < (d_rock_radius + d_missile_radius):
                remove = set([])
                remove.add(rock)
                explosion_group.add(rock)
                rock.animated = True
                rock_group.difference_update(remove)
                score += 50
        
# key handlers to control ship   
def keydown(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(True)
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot()
        
def keyup(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(False)
        
# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, lives, score, rock_group
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    
    if (not started) and inwidth and inheight:
        started = True
        lives = 3
        score = 0
        soundtrack.rewind()
        soundtrack.play()
        
        for rock in rock_group:
            remove = set([])
            remove.add(rock)
            rock_group.difference_update(remove)

def draw(canvas):
    global explosion_group, time, time_a, started, num_rock, lives

    if lives <= 0:
        started = False
        num_rock = 0
        lives = 0
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw UI
    canvas.draw_text("Lives", [50, 50], 22, "White")
    canvas.draw_text("Score", [680, 50], 22, "White")
    canvas.draw_text(str(lives), [50, 80], 22, "White")
    canvas.draw_text(str(score), [680, 80], 22, "White")
    
    #draw
    my_ship.draw(canvas)
    a_rock.draw(canvas)
    a_missile.draw(canvas)
    
    for missile in missile_group:
        missile.draw(canvas)
        missile.update()
    
    for rock in rock_group:
        rock.draw(canvas)
        rock.update()
        a_rock.collide(rock)
        
    for exp in explosion_group:
        exp.draw(canvas)
        exp.update()
    
    group_collide(rock_group, missile_group)
    
    # update ship and sprites
    my_ship.update()
    a_rock.update()
    a_missile.update()
    
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())

# timer handler that spawns a rock    
def rock_spawner():
    global num_rock, started, rock_group, a_rock
    rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
    rock_vel = [random.random() * .6 - .3, random.random() * .6 - .3]
    rock_avel = random.random() * .2 - .1
    a_rock = Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image, asteroid_info)
    
    if started:
        
        if num_rock < 25:
            a_rock = Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image, asteroid_info)
            num_rock += 1
            rock_group.add(a_rock)
        if num_rock > 24:
            num_rock += 1
            rock_group.add(a_rock)
            
    for missile in missile_group:
        if missile.lifespan:
            remove = set([])
            remove.add(missile)
            missile_group.difference_update(remove)    

# initialize stuff
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
a_rock = Sprite([WIDTH / 3, HEIGHT + 80], [0, 0], 0, 0, asteroid_image, asteroid_info)
a_missile = Sprite([2 * WIDTH / 3, 2 * HEIGHT / 3], [-1,1], 0, 0, missile_image, missile_info, missile_sound)
a_explosione = ([WIDTH / 3, HEIGHT / 3], [1, 1], 0, .1, explosion_image, explosion_info) 

# register handlers
frame.set_keyup_handler(keyup)
frame.set_keydown_handler(keydown)
frame.set_mouseclick_handler(click)
frame.set_draw_handler(draw)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
