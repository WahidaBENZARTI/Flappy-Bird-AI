import pygame #games and other multimedia applications
import neat #Neuroevolution of Augmented Technologies
import time
import os
import random #randomly place the height of the tube
pygame.font.init() #initilaize the font

#set the dimensions of the screen
WIN_WIDTH = 500 #Contant value that's why we use capital letters
WIN_HEIGHT = 800

#load the needed images
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))] #Double the size of the images
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 50) #set the font of the score writing

class Bird:
	IMGS = BIRD_IMGS
	MAX_ROTATION = 25 #how the bird needs to tilt up or down (in degrees)
	ROT_VEL = 20 #rotation velocity
	ANIMATION_TIME = 5

	def __init__(self, x, y): #self represents the instance of the class
		self.x = x #positions of the bird
		self.y = y
		self.tilt = 0
		self.tick_count = 0
		self.vel = 0
		self.height = self.y
		self.img_count = 0
		self.img= self.IMGS[0]

	def jump(self):
		self.vel = -10.5 #negative velocity for up jumping , positive velocity for down jumping
		self.tick_count = 0 #keep track of when we last jump
		self.height = self . y

	def move(self): #where we call every single frame to move our bird
		self.tick_count += 1

		d = self.vel*self.tick_count + 1.5*self.tick_count**2 #displacement in pixels
		#set the limits of velocity
		if d >=16:
			d = 16
		if d < 0:
			d -=2

		self.y = self.y + d #set the new position after displacement

		if d < 0 or self.y < self.height + 50: #if we're moving upwards, we're tilting the bird upwards
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION
		else: #if we're not moving upwards, we're tilting the bird downwards
			if self.tilt > -90:
				self.tilt -= self.ROT_VEL

	def draw (self, win): #win represents the window that we're doing to draw the bird on
		self.img_count +=1

		#select the bird image based on the current img_count
		if self.img_count < self.ANIMATION_TIME:
			self.img = self.IMGS[0]
		elif self.img_count < self.ANIMATION_TIME*2:
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*3:
			self.img = self.IMGS[2]
		elif self.img_count < self.ANIMATION_TIME*4:
			self.img = self.IMGS[1]
		elif self.img_count == self.ANIMATION_TIME*4 + 1:
			self.img = self.IMGS[0]
			self.img_count = 0

		if self.tilt <= -80:
			self.img =self.IMGS[1]
			self.img_count = self.ANIMATION_TIME*2

		#rotate an image around its center
		rotated_image = pygame.transform.rotate(self.img, self.tilt)
		new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
		win.blit(rotated_image, new_rect.topleft) #blit=draw on the window

	def get_mask(self): #we use when we get collision for our objects
		return pygame.mask.from_surface(self.img)

class Pipe:
	GAP = 200 #the space between the pipes
	VEL = 5 #the speed of the pipes, PS: the bird is not moving horizontally, just vertically, but all the objects are, that's why it looks like the bird is moving

	def __init__(self, x):
		self.x = x
		self.height = 0
		self.gap = 100
		#keep track of where the top/bottom of our pipe are gonna be drawn and 	
		self.top = 0
		self.bottom = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) #the top pipe should be 90 degree flipped
		self.PIPE_BOTTOM = PIPE_IMG

		self.passed = False #if the bird passed the pipe
		self.set_height() #define the pipe's caracteristics: length, direction..

	def set_height(self):
		self.height = random.randrange(50,450) #where we want the top of our pipe to actually be on the screen
		self.top = self.height - self.PIPE_TOP.get_height() #where the image will be cut in order to show only the wanted length of pipe
		self.bottom = self.height + self.GAP

	def move(self):
		#we need to move the pipe by changing th x posiion based on the velocity that the pipe should move each frame
		self.x -= self.VEL #move the pipe to the left

	def draw(self,win):
		win.blit(self.PIPE_TOP,(self.x, self.top))
		win.blit(self.PIPE_BOTTOM,(self.x, self.bottom))

	#collision: we're using MASKS in pygame to avoid the collision with boxes, just the colored pixels , so that the bird can actually touch the pipe and not juts ts window
	def collide(self, bird):
		bird_mask = bird.get_mask() #get the mask/colored pixels of the bird
		top_mask = pygame.mask.from_surface(self.PIPE_TOP) #get the mask of the top pipe
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM) #get the mask of the bottom pipe
		
		top_offset = (self.x - bird.x, self.top - round(bird.y)) #offset: how far away these masks are from each other
		#the round is because we can't use negative or decimal numbers
		bottom_offset = (self.x - bird.x, self.bottom- round(bird.y))

		#we need to figure out whether the masks collided or not= get the points of collision
		t_point = bird_mask.overlap(top_mask, top_offset) #collision bird-top pipe
		b_point = bird_mask.overlap(bottom_mask, bottom_offset) #collision bird-bottom pipe

		if t_point or b_point:
			return True

		return False

class Base:
	VEL = 5 #the base should be moving with the same speed as the pipes
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH
		#we're using two images of the base that move to the left one behind the other
	
	def move(self):
		self.x1 -= self.VEL #x1:the position of the first image changing every frame =base moving
		self.x2 -= self.VEL #x2:the position of the second image changing every frame =second image moving on the same speed as the first

		if self.x1 + self.WIDTH <0: #if the fist image reach its end, we put it behind the second one, and now the second image is on the screen
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH <0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))



def draw_window(win, birds, pipes, base, score):
	win.blit(BG_IMG, (0,0)) #set the backgrounf on the position O,O
	for pipe in pipes:
		pipe.draw(win)
	text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
	base.draw(win)

	for bird in birds: 
		bird.draw(win)

	pygame.display.update()


def main(genomes, config): #main is the genome evaluation function
	#birds= Bird(230,350) #position of the bird
	nets = []
	ge = []
	birds = []

	for _, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		birds.append(Bird(230,350))
		g.fitness = 0
		ge.append(g)


	base= Base (730) #position of the base at the botton of the screen
	pipes = [Pipe(600)]
	win= pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	clock = pygame.time.Clock()

	score = 0

	run = True
	while run:
		clock.tick(30) #30 ticks every second
		for event in pygame.event.get(): #keep track of the users intervention (mouse clicking..)
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()

		pipe_ind = 0 #indice of the pipe
		if len(birds) > 0:
			if len (pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): #if we passes the first pipe then we're looking for the second one
				pipe_ind = 1
		else: #no birds left, we should quit this generation
			run=False
			break

		for x, bird in enumerate(birds):
			bird.move()
			ge[x].fitness += 0.1 #the bird gain 1 fitness core every secod he stays alive
			output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
			
			if output[0] > 0.5:
				bird.jump()
		#bird.move()
		add_pipe= False
		rem = []
		for pipe in pipes:
			for x, bird in enumerate(birds):
				if pipe.collide(bird):
					ge[x].fitness -= 1 #when a bird collide with a pipe we should minimize its fitness score
					birds.pop(x) #remove the bird from the list
					nets.pop(x)
					ge.pop(x)

				if not pipe.passed and pipe.x < bird.x:
					pipe.passed = True
					add_pipe = True

			if pipe.x + pipe.PIPE_TOP.get_width() <0: #when the pipe is completely off the screen we need to remove it
				rem.append(pipe)

			pipe.move()

		if add_pipe:
			score += 1
			for g in ge:
				g.fitness += 5 #for the birds who passed the pipes we add 5 points to their fitness score

			pipes.append(Pipe(600))

		for r in rem:
			pipes.remove(r)

		for x, bird in enumerate(birds):
			if bird.y + bird.img.get_height() >= 730 or bird.y < 0: #if the bird hit the floor or supassed the screen on the top
					birds.pop(x) #remove the bird from the list
					nets.pop(x)
					ge.pop(x)

		base.move()
		draw_window(win, birds, pipes, base, score)



def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

	p = neat.Population(config) #setting the population
	#set the outputs
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	#set the fitness function
	winner = p.run(main,50)
	

if __name__=="__main__":
	local_dir= os.path.dirname(__file__)
	config_path= os.path.join(local_dir, "config-feedforward.txt")
	run(config_path)


























