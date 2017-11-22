import numpy as np 
import pygame as pg 
import PhyContact as contact

rint = np.random.randint

def randomColor(): 
	return (rint(10,200),rint(10,200),rint(10,200))

def scribe(n,v,wait = False): 
	print n + ': ' + str(v)
	if wait : raw_input()

class Vector(): 

	def __init__ (self, co = [0,0]):
		self.co = np.array(co).reshape(-1)
	def x(self): 
		return self.co[0]
	def y(self): 
		return self.co[1]
	def magn(self): 
		return np.sqrt(self.x()**2 + self.y()**2)
	def normalized(self):
		return Vector(self.co/self.magn())
	def xy(self): 
		return self.co  
	def Add(self, q): 
		self.co += q.co
	def dotProduct(self, b): 
		v = self.co.dot(b.co)
		return v 




class Particle(): 

	def __init__(self, p, mass = 1): 

		self.position = Vector(p)
		self.velocity = Vector([0,0])
		self.acc = Vector([0,0])

		self.accumlForces = Vector([0,0])

		self.mass = 1./mass if mass > 0 else 0.

		self.color = (rint(10,250),rint(10,250),rint(10,250))

	def draw(self,screen, screenSize): 

		position = self.scale(screenSize)
		pg.draw.circle(screen, self.color, position, 5)

	def scale(self, size):

		position = self.position.xy()
		position = position*100
		position[1] = size[1] - position[1]
		position = [int(position[0]), int(position[1])]
		return position

	def setSpeed(self, v): 
		self.velocity = Vector(v)
	def setAcc(self, v): 
		self.acc = Vector(v)

	def addSpeed(self, v): 
		self.velocity.Add(v)
	def addAcc(self, a): 
		self.acc.Add(v)

	def integration(self,a, drag = 1., time = 1./30):

		self.position.co = self.position.co + self.velocity.co*time
		self.acc.co = a.co + self.accumlForces.co*self.mass
		self.velocity.co = self.velocity.co*drag + time*self.acc.co
		
		self.clearAccumulator()

	def clearAccumulator(self): 
		self.accumlForces = Vector([0,0])

	def addForce(self, f): 
		self.accumlForces.co += f.co

	def setMass(self,m):
		if m == 0: 
			self.mass = 0.
		else: 
			self.mass = 1./m


class Shape(): 

	def __init__(self,shape,center, extends, color = randomColor()): 

		self.color = color
		self.shape = shape
		self.center = Vector(center)
		if shape == 'ball': 
			self.defineCircle(extends)
		else: 
			self.defineRect(extends)

	def defineRect(self, extends): 

		self.width = extends[0]/2.
		self.height = extends[1]/2.
		self.angle = extends[2]

		self.getPoints(self.center.co)

	def getPoints(self, center): 

		self.points = []
		inc = [[-1.,-1.], [-1.,1.], [1.,1.], [1.,-1.]]
		angle = np.radians(self.angle)
		for i in inc: 
		
			# ------- Axes ---------------
			d1 = np.array([np.cos(angle), np.sin(angle)])
			d2 = np.array([d1[1],-d1[0]])

			# -------- Vecteur ------------
			delta = d1*self.width*i[0] + d2*self.height*i[1]

			# -------- Calcul du coin from the center ---- 
			p = center + delta
			p = Vector(p)
			self.points.append(p)

		return self.points


	def defineCircle(self, extends): 

		self.radius = extends[0]

	def draw(self, screen, screenSize): 

		position = self.scale(screenSize)
		if(self.shape == 'ball'): 
			pg.draw.circle(screen, self.color, position, self.radius)
		else: 
			lines = self.getLines(position)
			pg.draw.lines(screen, self.color, True, lines, 10)

	def scale(self, size, factor = 100): 

		p = self.center.co
		p = p*factor
		p[1] = size[1] - p[1]
		p = [int(p[0]), int(p[1])]
		return p

	def getLines(self,position): 

		self.getPoints(position)
		points = self.points
		l = []
		for p in points: 
			l.append(p.co)
		l.append(points[0])
		return l


class Body(Particle): 

	def __init__(self, shape, mass = 1): 
		#super(Particle,self).__init__(shape.center.co)
		Particle.__init__(self, shape.center.co)
		self.shape = shape 

	def draw(self, screen, screenSize): 
		self.shape.draw(screen, screenSize)

	def step(self,a, drag = 1., time = 1./30):
		self.integration(a,drag, time)
		self.update()

	def update(self):
		self.shape.center.co = self.position.co

class WorldofParticles():

	def __init__(self, p, s,b, g = Vector([0,-10]), drag = 0.999): 

		self.gravity = g
		self.shapes = s
		self.bodies = b
		self.drag = drag
		self.particles = p

		self.itTime = 120

		self.initRender()

	def initRender(self, size = [1000,1000]):

		self.screenSize = size
		self.screen = pg.display.set_mode(self.screenSize)
		self.clock = pg.time.Clock()

	def render(self): 

		self.clock.tick(self.itTime/2) 
		self.screen.fill((0,0,0))
		for p in self.particles: 
			p.draw(self.screen, self.screenSize)

		for s in self.shapes: 
			s.draw(self.screen, self.screenSize)

		for b in self.bodies: 
			b.draw(self.screen, self.screenSize)

		pg.display.flip()

	def step(self): 
		for p in self.particles: 
			for pp in self.particles: 
				if p != pp: 
					self.checkCollision(p,pp)
			p.integration(self.gravity, time = 1./self.itTime, drag = self.drag)

		for b in self.bodies: 
			b.step(self.gravity, time = 1./self.itTime, drag = self.drag)

	def checkCollision(self, p1,p2): 
		pos1 = p1.position.co
		pos2 = p2.position.co 

		d = np.sum((pos1 - pos2)**2)
		if d < 0.003: 
			scribe('Collision', d)
			c = contact.Collision(p1,p2)


# p1 = Particle([0.1,0.1])
# p2 = Particle([5,1])
# p3 = Particle([1,9])

# p4 = Particle([2,5])
# p5 = Particle([4,5])

# p1.setSpeed([0.,10.])
# p2.setSpeed([5.,10.])
# p3.setSpeed([5.,10.])

# p4.setSpeed([5.,0.])
# p5.setSpeed([-5.,0.])

r1 = Shape('rect',[1,1], [50,20,0])
r2 = Shape('rect',[8,1], [150,20,45])
bb = Shape('ball', [1,5], [5])

r1 =  Body(r1)
r1.setSpeed([5,10])

b2 = Body(bb)
b2.setSpeed([0,5])

r2 = Body(r2)
r2.setSpeed([-5,10])

world = WorldofParticles([], [], [r1,b2,r2])

conteur = 0

while True: 
	world.render()
	world.step()

	conteur += 1
	if conteur == 30: 
		force = Vector([1000,100])
		r1.addForce(force)
	if conteur == 100: 
		force = Vector([-1000,500])
		r1.addForce(force)


