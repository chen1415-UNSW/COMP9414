
# agent.py
'''
Agent for Text-Based Adventure Game
COMP9414 Artificial Intelligence
UNSW Session 1, 2017

Yihan Xiao z5099956

This agent program works with 2 classes. A class of Block, which records
all information of a block we found, like its coordinate, type and whether
we have access from our current state. Anohter class of Agent, which is 
the major part of the programe, all state information restored in it.
The agent search the environment with comination of DFS and A*. It goes
every block seen around, and when need to search path to a certain block,
agent will compute the path with least cost. We use Manhattan distance as
heuristic function to do searching.

In order to make logic decision, we use a priority queue to arrange events.
Events are case like cutting a tree, openning a lock or so on. There are
quite a lot logical consideration involved in this task, for instance if 
agent dose not have a key, then it is unresonalbe to go to any lock; if
the agent has a raft and there is sea(water) eara arround, searching in 
sea becomes available. We assign different priorities to events and every 
time when the main function asks reponse from the agent, the event manager
will choose a event with highest priority(smallest in number) and this 
event will generate a list of order for the server to operate. If the order
list is not empty, the program will keep running without making further 
decisions until it is empty and then event manager will be activated again.

There are some "tricky" decisions along implementing the agent. For example,
the server will not tell us if the agent has a raft or any other tools. So
we have to "remember" all these information, and when several events share
the same resources, it is quite easy to mess up with them. Another typical
case is path searching. Sometimes the path will go cross the sea and then
arrive at an island, or pass by a land and enter the sea again. This is 
very dangerous because the program will keep running until the agent go
all the way along the path. We won't know if the agent lost raft in the 
middle of travel. To solve this, we have to anaylse the path after searching
and prevent all these cases from happening.
=========================================================================
'''
import sys
import socket
import time
from queue import PriorityQueue
from collections import deque
from collections import namedtuple

Event = namedtuple('Event','prior, name, para')
        
class Block(object):
    
    def __init__(self, pos, types):
        self.pos = pos # (x, y)
        self.types = types # road/wall/tree/sea/tool
        self.isOpen = False # accessible or not
        
        self.isGoal = False # if it is treasure
        self.isFrontier = True # edge of view, need exploring if true
        
        self.cost = float('inf') # record cost when search path
        
class Agent(object):
    
    def __init__(self):
        self.tools = [] # axe/dynamite/key/treasure
        self.tools_position = {} # store positions for tools found
        self.obstacle_position = {} # wood/lock/wall
        self.spot_position = {} # places where discover a tool or treasure
        self.event = PriorityQueue()
      
        self.current_pos = (0, 0)
        self.rotation = 'North' # change when the agent makes a turn
        self.rotation_dict = {'North':{(0,1):('','North'), (1,0):('r','East'), (0,-1):('rr','South'), (-1,0):('l','West')},
                              'East' :{(0,1):('l','North'), (1,0):('','East'), (0,-1):('r','South'), (-1,0):('ll','West')},
                              'South':{(0,1):('ll','North'), (1,0):('l','East'), (0,-1):('','South'), (-1,0):('r','West')},
                              'West' :{(0,1):('r','North'), (1,0):('rr','East'), (0,-1):('l','South'), (-1,0):('','West')}} 
        
        # cos & sin
        self.rotation_corr = {'North':(1,0), 'East':(0,1), 'South':(-1,0), 'West':(0,-1)}        
        
        self.world_map = {}
        self.start_pos = (0, 0)
        
        self.map_draw = [] # display module to show map
        self.map_width_floor = -1
        self.map_width_ceil = 1
        self.map_height_floor = -1
        self.map_height_ceil = 1
        
        self.action = deque()
        self.frontier = deque()
        
        self.inSea = False # if the agent is in sea now
        self.canSwim = False # if you have a wood
        
   
    # correcting coordinates from view   
    def rotation_correction(self, pos):
        angle = self.rotation_corr[self.rotation]
        x = pos[0]*angle[0] + pos[1]*angle[1]
        y = pos[1]*angle[0] - pos[0]*angle[1]
        return (x, y)
    # display discovered map on screen
    def draw_map(self):
        self.map_draw = [['?' for j in range(self.map_height_floor-1, self.map_height_ceil+2)] 
                              for i in range(self.map_width_floor-1, self.map_width_ceil+2)]
        for pos in self.world_map:
            self.map_draw[pos[0]][pos[1]] = self.world_map[pos].types #'T' if self.world_map[pos].isFrontier else 'N'
        
        my_arrow = {'North':'^', 'East':'>', 'South':'v', 'West':'<'}[self.rotation]
        self.map_draw[self.current_pos[0]][self.current_pos[1]] = my_arrow
                         
        for j in range(self.map_height_ceil+1, self.map_height_floor-2, -1):
            for i in range(self.map_width_floor-1, self.map_width_ceil+2):
                if j == 0 and i == 0: print('H',end='')
                else: print(self.map_draw[i][j],end='')
            print()
            
    # key function to explore the world in every step, this function
    # is mainly called in event_exploreMap
    def explore(self, view):
        # explore the world if possible
        for j in range(-2, 3):
            for i in range(2, -3, -1):
                local_x = j 
                local_y = i 
  
                if view[2-i][j+2] == '^': sign = ' '
                else: sign = view[2-i][j+2]
                # check the edge of map
                if sign == '.':
                    continue
                # add this pos to world map
                global_pos_shift = self.rotation_correction((local_x, local_y))
                global_pos = (self.current_pos[0]+global_pos_shift[0], self.current_pos[1]+global_pos_shift[1])
               
                if global_pos not in self.world_map:
                    # change the size of map displayed
                    if global_pos[0] > self.map_width_ceil: 
                        self.map_width_ceil = global_pos[0]
                    
                    if global_pos[0] < self.map_width_floor: 
                        self.map_width_floor = global_pos[0]                   
                    
                    if global_pos[1] > self.map_height_ceil:
                        self.map_height_ceil = global_pos[1]
                    
                    if global_pos[1] < self.map_height_floor:
                        self.map_height_floor = global_pos[1]    
                        
                    self.world_map[global_pos] = Block(global_pos, sign)
                    if sign in ['a', 'k', 'd', '$']: # this is a tool or treasure
                        if sign in self.tools_position:
                            self.tools_position[sign].append(global_pos)
                        else:
                            self.tools_position[sign] = [global_pos]
                        # remember the position where we see some stuff
                        if sign in self.spot_position:
                            self.spot_position[sign].append(self.current_pos)
                        else:
                            self.spot_position[sign] = [self.current_pos]
                            
                    elif sign in ['-', 'T', '*', '~']: # this is an obstacle
                        if sign in self.obstacle_position:
                            self.obstacle_position[sign].append(global_pos)
                        else:
                            self.obstacle_position[sign] = [global_pos]
                            
                    if i == 0 and j == 0: # current pos
                        self.world_map[global_pos].isOpen = True
        # connecting neighour
        self.find_neighour(self.current_pos)
        self.draw_map()
  
        # every time after giving an order, update the coordinate
        # and the direction of agent as well
        
    # connecting neighour so that we know which block is free to go next    
    def find_neighour(self, pos):
        if self.world_map[pos].isOpen:  # this pos is accessible
            for pos_shift in [(0,1), (1,0), (0,-1), (-1,0)]:
                # make all its neighbour accessible
                this_pos = (pos[0]+pos_shift[0], pos[1]+pos_shift[1])
                if this_pos in self.world_map:
                    if not self.world_map[this_pos].isOpen:                    
                        if self.world_map[this_pos].types not in ['*', '~']:
                            self.world_map[this_pos].isOpen = True
                            # recurse to connect other block
                            if self.world_map[this_pos].types not in ['-', 'T']:
                                self.find_neighour(this_pos)
    
    # measure distance with Manhattan distance
    def distance(self, pos1, pos2):
        return abs(pos2[0]-pos1[0]) + abs(pos2[1]-pos1[1])                       
                    
    # go to a specific block
    def go_to_block(self, pos, thrSea=False, thrObs=False, ObsNum=0, ObsType=['*','T'], ObsExc=['~']):
        # check if this block is accessible
        if not thrObs:
            if not self.world_map[pos].isOpen:
#                print('Blcok',pos,'not accessible')
                return 
        # check if the goal is just current position
        if self.current_pos == pos:
            print('You are at goal now!')
            return 

        # search for a possible path
        def search_next(cur_pos, goal_pos, step_list, cost, thrSea):
#            if goal_pos == (0,0): print(step_list)
            next_pos_list = [] 
            for pos_shift in [(0,1), (1,0), (0,-1), (-1,0)]:
                next_pos = (cur_pos[0]+pos_shift[0], cur_pos[1]+pos_shift[1])
                if next_pos in self.world_map:
                    if thrSea:
                        if self.world_map[next_pos].isOpen and self.world_map[next_pos].types == '~':
                            next_pos_list.append((next_pos, self.distance(goal_pos,next_pos)))
                    else:
                        if self.world_map[next_pos].isOpen and self.world_map[next_pos].types not in ['T', '-']:
                            next_pos_list.append((next_pos, self.distance(goal_pos,next_pos)))
                        elif next_pos == goal_pos:
                            next_pos_list.append((next_pos, self.distance(goal_pos,next_pos)))
                            
            # if no where to go(dead end), return
            if len(next_pos_list) == 0:
                return      
            # starting from the pos with least distance
            next_pos_list.sort(key = lambda x : x[1])
            
            for next_pos_d in next_pos_list:
                next_pos = next_pos_d[0]
                if next_pos not in step_list: # avoid loop
                    # if destination reached
                    if next_pos == goal_pos:
                        step_list.append(next_pos)
                        return step_list
                    # or continue to search
                    # compare cost from other path
                    # always record the smallest cost
                    elif self.world_map[next_pos].cost > cost:
                        self.world_map[next_pos].cost = cost
                        new_step_list = step_list.copy()
                        new_step_list.append(next_pos)               
                        path = search_next(next_pos, goal_pos, new_step_list, cost+1, thrSea)
                        if path != None: # find a path
                            return path
       
        # search for a possible path through obstacle
        # this function is basically the same with search_next
        # except it mainly search for path through obstacles (for use of dynimtes)
        def search_next_Obs(cur_pos, goal_pos, step_list, cost, ObsNum, ObsType=['*','T'], ObsExc=['~']):
            next_pos_list = []
            for pos_shift in [(0,1), (1,0), (0,-1), (-1,0)]:
                next_pos = (cur_pos[0]+pos_shift[0], cur_pos[1]+pos_shift[1])
                if next_pos in self.world_map:
                    if self.world_map[next_pos].types not in ObsExc:
                        next_pos_list.append((next_pos, self.distance(goal_pos,next_pos)))
            # if no where to go(dead end), return
            if len(next_pos_list) == 0:
                return      
            # starting from the pos with least distance
            next_pos_list.sort(key = lambda x : x[1])
            
            for next_pos_d in next_pos_list:
                next_pos = next_pos_d[0]
                if next_pos not in step_list:
                    # destination reached
                    if next_pos == goal_pos:
                        step_list.append(next_pos)
                        return step_list
                    # compare cost 
                    elif self.world_map[next_pos].cost > cost:
                        self.world_map[next_pos].cost = cost
                        # continue to search
                        new_step_list = step_list.copy()
                        new_step_list.append(next_pos)
                        path = None
                        if self.world_map[next_pos].types in ObsType:
                            # this block is an obstacle
                            if ObsNum-1 >= 0:
                                path = search_next_Obs(next_pos, goal_pos, new_step_list,
                                               cost+1, ObsNum-1, ObsType, ObsExc)
                        else:
                             path = search_next_Obs(next_pos, goal_pos, new_step_list,
                                               cost, ObsNum, ObsType, ObsExc)
                        if path != None: # find a path
                            return path     
                    # if cost of other paths when get here is smaller, no need to expand
                    # this path. We only want the path with cost as small as possible

        if thrObs == False:
             # initialize all path cost inf
             # cost here is number of steps to reach current block
            for block in self.world_map.values():
                block.cost = float('inf')
            path = search_next(self.current_pos, pos, [], 0, thrSea)
        else:
            # initialize all path cost inf
            # cost here is number of tools used to reach current block
            for block in self.world_map.values():
                block.cost = float('inf')
            # search path with obstacles
            path = search_next_Obs(self.current_pos, pos, [],
                               0, ObsNum, ObsType, ObsExc)
        if path != None:
            print('Path found')
            print('Goal', pos, self.world_map[pos].types)

        else:
            print('No path', pos, self.world_map[pos].types, self.world_map[pos].isOpen)
           
        return path
            
    # make turn(rotate agent)     
    def make_turn(self, dif_pos):
        return self.rotation_dict[self.rotation][dif_pos]
    
    # key function to generate order to game server    
    def order_generate(self, path, event=None):
        assert path != [] and path != None
                       
        order_string = ''
        order_result = []
        for pos in path:
            # check if the path end with a tool
            if self.world_map[pos].types in ['k', 'd', 'a', '$']:
                # add tool to agent item list
                this_tool = self.world_map[pos].types
                self.tools.append(this_tool)
                # delete the tool from map and tool dict
                self.tools_position[this_tool].remove(pos)
                self.world_map[pos].types = ' '

            dif_pos = (pos[0]-self.current_pos[0], pos[1]-self.current_pos[1])
            turn = self.make_turn(dif_pos)
            order_string += turn[0] # make a turn
            for order in turn[0]:
                order_result.append(turn[1])
            #-------------Event--------------------
            if pos == path[-1]: # last block, see if should do something
                if event == 'unlock':
                    order_string += 'u'
                    # delete this lock from map and lock dict
                    self.world_map[pos].types = ' ' 
                    self.world_map[pos].isOpen = True
                    self.obstacle_position['-'].remove(pos)
                elif event == 'cut':
                    order_string += 'c'
                    # add wood to tools
                    self.tools.append('w')
                    # delte this tree from map
                    self.world_map[pos].types = ' '
                    self.world_map[pos].isOpen = True
                    self.obstacle_position['T'].remove(pos)
                    
            if self.world_map[pos].types in ['*','T']:
                if event == 'boom':
                    order_string += 'b'
                    # delete this obstacle from map
                    self.obstacle_position[self.world_map[pos].types].remove(pos)
                    self.world_map[pos].types = ' '
                    self.world_map[pos].isOpen = True
                    self.tools.remove('d')
                    order_string += 'f' # move step forward
                    order_result.append(pos)
                    # updata current location and direction         
                    self.rotation = turn[1]
                    self.current_pos = pos                   
                    break
            
            #--------------------------------------
            order_string += 'f' # move step forward
            order_result.append(pos)
          
            # updata current location and direction         
            self.rotation = turn[1]
            self.current_pos = pos
           
            # remove frontier label from this pos
            self.world_map[pos].isFrontier = False
          
        for com in order_string:
            self.action.append(com)
    # exploring world with DFS+A* 
    # keep exploring if there's block to go              
    def event_exploreMap(self, view):
        # record view first
        self.explore(view)
        # if agent is in sea, always set all sea block free to go           
        if self.inSea:
            for sea_pos in self.obstacle_position['~']:
                self.world_map[sea_pos].isOpen = True
        
        # set frontier: frontier is block which has not visited yet
        for pos_shift in [(-1,0), (0,-1), (1,0), (0,1)]:
            frontier_pos = (self.current_pos[0]+pos_shift[0],self.current_pos[1]+pos_shift[1])
            if frontier_pos in self.world_map:
                if self.inSea == False: # only search on land
                    if (self.world_map[frontier_pos].isOpen and 
                        self.world_map[frontier_pos].isFrontier and 
                        self.world_map[frontier_pos].types not in ['-','~','T']
                        ):
                        self.frontier.appendleft(frontier_pos)
                else: # only search in sea
                    if (self.world_map[frontier_pos].types == '~' and 
                        self.world_map[frontier_pos].isFrontier
                        ):
                        self.frontier.appendleft(frontier_pos)
        
        # if nowhere to go, return
        if len(self.frontier) == 0:
            print('Exploration finish') 
            return 0
        # pick a frontier to go and explore
        path = None
        while len(self.frontier) > 0:
            next_frontier = self.frontier.popleft()
            if self.world_map[next_frontier].isFrontier:
               print('Go to Frontier:',next_frontier,self.world_map[next_frontier].types)
               
               path = self.go_to_block(next_frontier, self.inSea) 
               break
        
        if path == None:
            print('Exploration finish') 
            return 0
        else:
            self.order_generate(path)
            return 1
    # switch exploring in sea or land
    # this is very important, we have to deal with wood(raft)
    # and we do not want cases that agent choose a path through
    # sea and land at the same time. Because we can not get response
    # from the sever what tool we have, we have to keep track all tools
    # especially wood, oterwise it is highly likey to fail.
    def event_switchExp(self, target_pos=None):
        path = None
        if not self.inSea: # go to sea to explore
            sea_entry = []
            for sea_pos in self.obstacle_position['~']:
                sea_entry.append((sea_pos, self.distance(self.current_pos, sea_pos)))
            if len(sea_entry) > 0:
                sea_entry.sort(key = lambda x : x[1])    
                for sea_pos_d in sea_entry:
                    path = self.go_to_block(sea_pos_d[0])
                    if path != None: break
                
            if path != None:
                self.order_generate(path, event='explore_switch')
                self.inSea = True
                return 1
            else:
                return 0
        else: # go to land to explore
            # first check if we found any tool when we are in sea
            if target_pos == None:
                for tool, tool_pos_list in self.tools_position.items():
                    if tool == 'k' and len(tool_pos_list) > 0:
                        target_pos = tool_pos_list[0]
                        break
                    elif tool == 'd' and len(tool_pos_list) > 0:       
                        target_pos = tool_pos_list[0]
                        break
                    elif tool == '$' and len(tool_pos_list) > 0:
                        target_pos = tool_pos_list[0]
                        break
            # go to the position of sea which is nearst to target
            sea_tar_dis = []
            for sea_pos in self.obstacle_position['~']:
                sea_tar_dis.append((sea_pos, self.distance(target_pos, sea_pos)))
            sea_tar_dis.sort(key= lambda x : x[1])

            for sea_pos_d in sea_tar_dis:
                path = self.go_to_block(sea_pos_d[0], True)
                if path != None: break
            
            if path != None:
                self.order_generate(path, event='explore_switch')
                # then find the shortest path to goal
                land_tar_list = []
                for land_pos, block in self.world_map.items():
                    if block.types == ' ':
                        land_tar_list.append((land_pos, self.distance(target_pos, land_pos)))
                land_tar_list.sort(key= lambda x : x[1])
                for land_pos_d in land_tar_list:
                    path_con = self.go_to_block(land_pos_d[0])
                    if path_con != None:
                        self.order_generate(path_con)
                        self.inSea = False
                        self.tools.remove('w')
                        print('Remove tree')
                        return 1
            else:
                return 0
            
    # if we have got treasure, return to start position        
    def event_return(self):
        path = None
        if 'w' in self.tools and not self.inSea:
            if '~' in self.obstacle_position:
                for sea_pos in self.obstacle_position['~']:
                    self.world_map[sea_pos].isOpen = True
                                  
        if '$' in self.tools:
            path = self.go_to_block((0,0))
            if path != None:
               
                for step_pos in path:
                    if '~' in self.obstacle_position:
                        if step_pos in self.obstacle_position['~']:
                            # agent has to cross sea, check if there's wood
                            if 'w' not in self.tools:
                                return 0
                            else:
                                self.order_generate(path)
                                print('Congratulations!')
                                return 1
                # lucky, no need to cross sea
                self.order_generate(path)
                print('Congratulations!')
                return 1
            else:
                return 0
    
    # if we have got a key, open a lock we found        
    def event_openLock(self): 
        if '-' in self.obstacle_position:
            path = None
            for lock_pos in self.obstacle_position['-']:
                path = self.go_to_block(lock_pos)
                if path != None: break
            if path != None:
                if not self.inSea:
                    for step in path:
                        if self.world_map[step].types == '~':
                            if 'w' in self.tools:
                                self.tools.remove('w')
#                            self.event.put(Event(1, 'Switch_Explore', lock_pos))
                                
                self.order_generate(path, event='unlock')
                return 1
            else:
                return 0
        else:
            return 0
        
    # if we found any tool, try to get it    
    def event_getTool(self, tool):
        assert tool != None
        path = None
        num_bomb = sum([1 if t == 'd' else 0 for t in self.tools])
      
        print('tool to go',tool)
        for tool_pos, spot_pos in zip(self.tools_position[tool], self.spot_position[tool]):
#        tool_pos = self.tools_position[tool][0]
#        spot_pos = self.spot_position[tool][0]
       
            self.world_map[tool_pos].isOpen = True
            # go to the nearst position first (the position we see it)
            path = self.go_to_block(spot_pos)
            if path != None: 
                for step in path:
                    if self.world_map[step].types == '~':
    #                        if 'w' in self.tools:
    #                            self.tools.remove('w')
                        self.event.put(Event(1, 'Switch_Explore', tool_pos))
                        return 0
                self.order_generate(path)
                path_obs = self.go_to_block(tool_pos, thrObs=True, ObsNum=num_bomb)
                if path_obs != None:
                    self.order_generate(path_obs, event='boom')
                    return 1
                else:
                    return 0
            else:
                path_obs = self.go_to_block(tool_pos, thrObs=True, ObsNum=num_bomb)
                if path_obs != None:
                    self.order_generate(path_obs, event='boom')
                    return 1
                else:
                    return 0
    
    # cut a tree if needed
    def event_cutTree(self):
        path = None
        # find a tree
        tree_list = []
        for tree_pos in self.obstacle_position['T']:
            tree_list.append((tree_pos, self.distance(self.current_pos, tree_pos)))
        tree_list.sort(key= lambda x : x[1])
        for tree_pos_d in tree_list:
            path = self.go_to_block(tree_pos_d[0])
            if path != None: break
        if path != None:
            if not self.inSea:
                for step in path:
                    if self.world_map[step].types == '~':
                        if 'w' in self.tools:
                            self.tools.remove('w')
                            
            self.order_generate(path, event='cut')                     
            return 1
        else:
            return 0
    
    # use dynimtes, may needed when go home or get tool    
    def event_boomWay(self):
        num_bomb = sum([1 if item=='d' else 0 for item in self.tools])
        print('Booms',num_bomb)
        path = self.go_to_block((0,0), thrObs=True, ObsNum=num_bomb)
        if path != None:
            self.order_generate(path, event='boom')
            return 1
        else:
            return 0
    
    # key function to arrange all events logically      
    def event_check(self, exp_flag):
        # important, if agent dose not have wood, sea is not accessible
        if 'w' not in self.tools:
                if '~' in self.obstacle_position:
                    for sea_pos in self.obstacle_position['~']:
                        self.world_map[sea_pos].isOpen = False
 
        if '$' in self.tools: # if find treasure, take it home immediately
            self.event.put(Event(0, 'Return_Home', None))
        if exp_flag == 0: # exploring finish
            if 'k' in self.tools:
                if '-' in self.obstacle_position:
                    if len(self.obstacle_position['-']) > 0:
                        self.event.put(Event(1, 'Open_Lock', None))
            if 'd' in self.tools:
                if len(self.tools_position) > 0:
                     # different tools have different priorities
                    for tool, positions in self.tools_position.items():
                        if tool == 'k':
                            if len(positions) > 0:
                                self.event.put(Event(2, 'Get_Tool_K', None))
                        if tool =='d':
                            if len(positions) > 0:
                                self.event.put(Event(2, 'Get_Tool_D', None))
                        if tool == 'a':
                            if len(positions) > 0:
                                self.event.put(Event(2, 'Get_Tool_A', None))
                        if tool == '$':
                            if len(positions) > 0:
                               self.event.put(Event(2, 'Get_Tool_T', None))
                    
                if '$' in self.tools:
                    self.event.put(Event(5, 'Boom_Way', None))
            if 'a' in self.tools:
                if 'T' in self.obstacle_position:
                    if len(self.obstacle_position['T']) > 0 and 'w' not in self.tools:
                        self.event.put(Event(3, 'Cut_Tree', None))
            if 'w' in self.tools and not self.inSea:
                if '~' in self.obstacle_position:
                    for sea_pos in self.obstacle_position['~']:
                        self.world_map[sea_pos].isOpen = True
                    self.event.put(Event(4, 'Switch_Explore', None))
           
                                      
            if self.inSea:
                self.event.put(Event(4, 'Switch_Explore', None))
                   
           
    #-------------------------Action------------------------#    
    def get_action(self, view):
        # AI run
        # test
        
        if len(self.action) == 0:
           
            print('Tools found at',self.tools_position)
            print('We have:',self.tools)
            exp_flag = self.event_exploreMap(view)
            
            self.event_check(exp_flag)
            event_flag = 0
            
            while(not self.event.empty()):
                
                next_event = self.event.get()
            
                if next_event.name == 'Return_Home':
                    event_flag = self.event_return()
                    if event_flag == 1: 
                        print(next_event.name,'***Succeed***')
                        break # event succeed
                if next_event.name == 'Open_Lock':
                    event_flag = self.event_openLock()
                    if event_flag == 1: 
                        print(next_event.name,'***Succeed***')
                        break # event succeed
                if next_event.name == 'Get_Tool_K':
                    event_flag = self.event_getTool('k')
                    if event_flag == 1: 
                        print(next_event.name,'***Succeed***')
                        break # event succeed
                if next_event.name == 'Get_Tool_D':
                    event_flag = self.event_getTool('d')
                    if event_flag == 1: 
                        print(next_event.name,'***Succeed***')
                        break # event succeed
                if next_event.name == 'Get_Tool_T':
                    event_flag = self.event_getTool('$')
                    if event_flag == 1: 
                        print(next_event.name,'***Succeed***')
                        break # event succeed
                if next_event.name == 'Get_Tool_A':
                    event_flag = self.event_getTool('a')
                    if event_flag == 1: 
                        print(next_event.name,'***Succeed***')
                        break # event succeed
                if next_event.name == 'Cut_Tree':
                    event_flag = self.event_cutTree()
                    if event_flag == 1: 
                        print(next_event.name,'***Succeed***')
                        break # event succeed
                if next_event.name == 'Switch_Explore':
                    event_flag = self.event_switchExp(next_event.para)
                    if event_flag == 1: 
                        print(next_event.name,'***Succeed***')
                        break # event succeed
                if next_event.name == 'Boom_Way':
                    event_flag = self.event_boomWay()
                    if event_flag == 1: 
                        print(next_event.name,'***Succeed***')
                        break # event succeed       
                    
                if event_flag == 0: # event fail, go exploring
                    print(next_event.name,'---Fail---')
        
            if len(self.action) > 0:
                action = self.action.popleft()
                return action
                
            else:
                action = input("Enter Action(s): ").strip()
                if action in [char for char in "FLRCUBflrcub"]:
                    return action
        else:
            action = self.action.popleft()
            return action

      
        #--------------------------------------------------------#
         

    def print_view(self, view,):
        print("\n+-----+")
        for row in range(5):
            print("|", end="")
            for col in range(5):
                print(view[row][col], end="")
            print("|")
        print("+-----+")


def main(port):
#    if len(sys.argv) < 2:
#        print("Usage: python agent.py -p <port>")
#        sys.exit(-1)
    # change way to launch 
#    server_port = int(sys.argv[2])
    server_port = port
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", server_port))

    agent = Agent()

    num_cells = 0
    cur_view = ""
    while True:
        data = client_socket.recv(1).decode('utf-8')
        if data == "":
            break
        num_cells += len(data)
        cur_view += data
        if num_cells == 12:
            cur_view += "^"
            num_cells += 1
        if num_cells < 25:
            continue
        view = [ [cur_view[row*5 + col] for col in range(5)] for row in range(5)]
        num_cells = 0
        cur_view = ""
#        agent.print_view(view)
        action = agent.get_action(view)
        # sleep for a while for observation
        time.sleep(0.05)
        client_socket.sendall(action.encode('utf-8'))


if __name__ == "__main__":
    main(2000)
    

# %% test2
L1 = [1,2,3,4]
L2 = [3,4,5,6]
for i,j in zip(L1,L2):
    print(i,j)