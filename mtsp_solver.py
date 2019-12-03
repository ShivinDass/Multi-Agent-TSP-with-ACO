import pygame,random,copy,math,sys


display_width=500
display_height=500

pygame.init()
gameDisplay=pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Game Window')
clock=pygame.time.Clock()


#######COLOR DEFINITION#########
Red=(255,0,0)
Blue=(0,0,255)
Green=(0,255,0)
Black=(0,0,0)
Yellow=(255,255,0)


################################
class group:
	def __init__(self):
		self.members=[]
		self.targetsNotVisited=set([])


	def addAgent(self,A):
		self.members.append(A)

	def initializeTSet(self):
		for i in range(numberTargets):
			self.targetsNotVisited.add(i)

	def totalLength(self):
		S=0
		for j in range(numberDepots):
			S+=self.members[j].lengthTravelled()
		return S


class Agent:
	def __init__(self,startSpot):
		self.radius=5
		self.startSpot=startSpot
		self.x=depots[startSpot].x
		self.y=depots[startSpot].y
		self.path=[startSpot+numberTargets]
		self.fuel=depots[startSpot].fuel

	def update(self,x_pos,y_pos):
		self.x=x_pos
		self.y=y_pos

	def display(self):
		pygame.draw.circle(gameDisplay,Green,(self.x,self.y),self.radius)

	def reset(self):
		self.x=depots[self.startSpot].x
		self.y=depots[self.startSpot].y
		self.path=[self.startSpot+numberTargets]
		self.fuel=depots[self.startSpot].fuel

	def addToPath(self,t):
		self.path.append(t)

	def getCurrentPos(self):
		return self.path[len(self.path)-1]

	def lengthTravelled(self):
		totalD=0
		for i in range(len(self.path)-1):
			totalD+=distance[min(self.path[i],self.path[i+1])][max(self.path[i],self.path[i+1])]
		return totalD


class targ:
	def __init__(self,x,y):
		self.radius=10
		self.x=x
		self.y=y

	def display(self):
		pygame.draw.circle(gameDisplay,Red,(self.x,self.y),self.radius)

	def dist(self, loc):
		return ((self.x-loc.x)**2+(self.y-loc.y)**2)**0.5


class depo:
	def __init__(self,x,y,f):
		self.radius=10
		self.x=x
		self.y=y
		self.fuel=f
		#self.agents=[]

	def display(self):
		pygame.draw.circle(gameDisplay,Blue,(self.x,self.y),self.radius)

	def dist(self, loc):
		return ((self.x-loc.x)**2+(self.y-loc.y)**2)**0.5



def initialize_targets(numberTargets):
	t=[]
	i=0
	while i<numberTargets:
		X=targ(random.randrange(10,display_width-10),random.randrange(10,display_height-10))
		flag=1
		for j in range(len(t)):
			if X.dist(t[j])<30:
				flag=0
				break
		if flag==1:
			t.append(copy.deepcopy(X))
			i+=1
	return t;



def initialize_depots(numberDepots):
	d=[]
	f=500
	i=0
	while i<numberDepots:
		X=depo(random.randrange(10,display_width-10),random.randrange(10,display_height-10),800)#random.randrange(500,600))
		flag=1
		for j in range(len(targets)):
			if X.dist(targets[j])<30:
				flag=0
				break
		for j in range(len(d)):
			if X.dist(d[j])<30:
				flag=0
				break
		if flag==1:
			d.append(copy.deepcopy(X))
			i+=1
	return d;


def drawMap():
	for i in range(numberTargets+numberDepots):
		for j in range(numberTargets+numberDepots):
			if j>i:
				concentration=math.floor(0.000001*(pheromone[i][j]**3)*distance[i][j])+1
				x1=targAndDep[i].x
				y1=targAndDep[i].y
				x2=targAndDep[j].x
				y2=targAndDep[j].y
				x3=(x2-x1)/concentration
				y3=(y2-y1)/concentration
				for k in range(0,concentration):
					pygame.draw.circle(gameDisplay,Yellow,(math.floor(k*x3+x1),math.floor(k*y3+y1)),1)


	for i in range(numberTargets):
		targets[i].display()

	for i in range(numberDepots):
		depots[i].display()


def resetPositions():
	for i in range(numberAgents):
		for j in range(numberDepots):
			Agents[i].members[j].reset()



def updatePheromone():
	Q=1000*numberDepots
	phro=0.5

	delta_pheromone=[]
	delta_stayProb=[0]*(numberDepots+numberTargets)
	for i in range(numberTargets+numberDepots):
		X=[0]*(numberDepots+numberTargets)
		delta_pheromone.append(X)
		

	for i in range(numberAgents):
		totalL=Agents[i].totalLength()
		totalL+=200*len(Agents[i].targetsNotVisited)
		q=Q/totalL 
		for j in range(numberDepots):
			if Agents[i].members[j].lengthTravelled()<=0:
				continue
			path=Agents[i].members[j].path
			prev=-1
			for k in range(len(path)-1):
				if not path[k]==path[k+1]:
					delta_pheromone[min(path[k],path[k+1])][max(path[k],path[k+1])]+=q
				else:
					delta_stayProb[path[k]]+=q
					prev=path[k]				

	for i in range(numberTargets+numberDepots):
		for j in range(i,numberTargets+numberDepots):
			pheromone[i][j]=phro*pheromone[i][j]+delta_pheromone[i][j]
		stayProb[i]=phro*stayProb[i]+delta_stayProb[i]
	return;


def choose(i,j,degrade):
	mew=0.7
	if len(Agents[i].targetsNotVisited)>0:
		S=0
		current=Agents[i].members[j].getCurrentPos()
		D=1000
		for k in Agents[i].targetsNotVisited:
			S+=(pheromone[min(current,k)][max(current,k)]/((distance[min(current,k)][max(current,k)])**mew))
			D=min(D,distance[min(current,k)][max(current,k)])
		S+=degrade*(stayProb[current])/(D**mew)

		r=random.random()
		p=0
		for k in Agents[i].targetsNotVisited:
			p+=(pheromone[min(current,k)][max(current,k)]/(distance[min(current,k)][max(current,k)]**mew))/S
			if r<=p:

				if Agents[i].members[j].fuel<distance[min(current,k)][max(current,k)]:
					

					#######REPLACE THIS LOOP#########
					checkOtherCityAvailable=False
					for kk in Agents[i].targetsNotVisited:
						if Agents[i].members[j].fuel>distance[min(current,kk)][max(current,kk)]:
							checkOtherCityAvailable=True
							break
					if not checkOtherCityAvailable:
						fuelFinished[j]=1
						Agents[i].members[j].addToPath(current)
					##################################

					if current<numberTargets:
						return targets[current]
					else:
						return depots[current-numberTargets]
				else:
					Agents[i].targetsNotVisited.remove(k)
					Agents[i].members[j].addToPath(k)
					Agents[i].members[j].fuel-=distance[min(current,k)][max(current,k)]
					return targets[k]

		Agents[i].members[j].addToPath(current)
		if current<numberTargets:
			return targets[current]
		else:
			return depots[current-numberTargets]

	return targ(-1,-1)



def game_loop(duration, group):
	quit=False
	xinit=[]
	yinit=[]
	x=[]
	y=[]
	for j in range(numberDepots):
		xinit.append(Agents[group].members[j].x)
		yinit.append(Agents[group].members[j].y)
		if choice[j].x>=0: 
			x.append((choice[j].x-Agents[group].members[j].x)/duration)
			y.append((choice[j].y-Agents[group].members[j].y)/duration)
		else:
			x.append(0)
			y.append(0)

	for t in range(duration):
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				quit=True
				pygame.quit()
		if quit:
			break

		gameDisplay.fill(Black)
		#######################DISPLAY########################

		drawMap()

		for j in range(numberDepots):
			Agents[group].members[j].update(math.floor(x[j]*t+xinit[j]),math.floor(y[j]*t+yinit[j]))
			Agents[group].members[j].display()

		pygame.display.update()
		clock.tick(1000)



seed=5
if len(sys.argv)>1:
	seed=int(sys.argv[1])
random.seed(seed)

numberTargets=15
numberDepots=4
numberAgents=50

randomizeDestinations=1#int(input("Press 1 to randomize:"))
targets=[]
depots=[]
if randomizeDestinations==1:
	targets=initialize_targets(numberTargets)
	depots=initialize_depots(numberDepots)
else:
	#A=[[0,0],[1,0],[2,0]]
	#T=[[1,2],[0,3],[3,3],[1,5],[4,5],[-2,4]]
	A= [[1, -5], [-3, 3], [4, 4]]
	T= [[0, -2], [0, 4], [-1, 0], [-2, 4], [4, 5], [-1, 5]]
	
	numberDepots=len(A)
	numberTargets=len(T)
	scale=50
	for i in T:
		targets.append(targ(i[0]*scale+math.floor(display_width/2),i[1]*scale+math.floor(display_height/2)))

	for i in A:
		depots.append(depo(i[0]*scale+math.floor(display_width/2),i[1]*scale+math.floor(display_height/2),10*scale))



Agents=[]
print()
for i in range(numberAgents):
	g=group()
	for j in range(numberDepots):
		X=Agent(j)
		g.addAgent(X)
	Agents.append(g)


targAndDep=[]
for i in range(numberTargets):
	targAndDep.append(targets[i])
for i in range(numberDepots):
	targAndDep.append(depots[i])


pheromone=[]
stayProb=[1]*(numberTargets+numberDepots)
for i in range(numberTargets+numberDepots):
	X=[1]*(numberDepots+numberTargets)
	pheromone.append(X)


distance=[]
for i in range(numberTargets+numberDepots):
	X=[]
	for j in range(numberDepots+numberTargets):
		X.append(targAndDep[i].dist(targAndDep[j]))
	distance.append(X)

fuelFinished=[0]*numberDepots

while 1>0:
	count=0
	for i in range(numberAgents):
		Agents[i].initializeTSet()
		deg=1
		exit=False
		fuelFinished=[0]*numberDepots

		
		while not exit:
			if len(Agents[i].targetsNotVisited)<=0 or sum(fuelFinished)==numberDepots:
				exit=True
			count+=1
			bef=len(Agents[i].targetsNotVisited)
			choice=[]
			for j in range(numberDepots):
				choice.append(choose(i,j,deg))

			if count%350==0:
				count=0
				game_loop(1,i)
			if len(Agents[i].targetsNotVisited)==bef:
				deg=0.8*deg
			else:
				deg=1

	for a in Agents[0].members:
		print(a.fuel,end=' ')
	print()

	updatePheromone()
	resetPositions()
pygame.quit()