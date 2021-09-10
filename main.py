import sys
import math

# height: size of the map
width, height = [int(i) for i in input().split()]


class Cell:
    # {(3,5): cell, (4,8): cell...}
    CELLS = dict()
    COORD_RADARS = [
        (4, 3), (4,11),
        (9, 7), 
        (14, 3), (14, 11), 
        (20, 7), 
        (9, 0), (9, 14),
        (25, 3), (25, 11),
        (28, 7), 
        (20, 0), (20, 14),
        (28, 1), (28, 14),
    ]
    NEXT_RADAR = -1
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ore = 0
        self.has_radar = False
        self.has_bomb = False
        self.has_hole = False
        self.safe = True

    @property
    def right(self):
        return Cell.get(self.x + 1, self.y)
    
    @property
    def adjacents(self):
        adjacents = [
            Cell.get(self.x - 1, self.y),
            self.right,
            Cell.get(self.x, self.y - 1),
            Cell.get(self.x, self.y + 1),
        ]
        return [_ for _ in adjacents if _]  # Remove None

    @property
    def harvestable(self):
        return self.ore > 0 and self.has_bomb is False and self.safe is True

    def path_to(self, other_cell):
        # find x
        if self.x < other_cell.x:
            x = self.x + 1
        elif self.x > other_cell.x:
            x = self.x - 1
        else:
            x = self.x
        # find y
        if self.y < other_cell.y:
            y = self.y + 1
        elif self.y > other_cell.y:
            y = self.y - 1
        else:
            y = self.y
        return x, y

    def distance(self, other_cell):
        return abs(self.x - other_cell.x) + abs(self.y - other_cell.y)
    
    def adjacent_with_ore(self):
        for cell in self.adjacents:
            if cell.ore and cell.ore > 0 and cell.has_bomb is False and cell.safe:
                return cell
    
    def closest_ore(self, min_ore=1):
        cells_with_ore = Cell.get_ore(min_ore=min_ore)
        cells_with_ore.sort(key=lambda x: self.distance(x))
        if cells_with_ore:
            return cells_with_ore[0]
        else:
            return None

    def update_from_input(self, inputs):
        ore = inputs[2*self.x]
        hole = inputs[2*self.x+1]
        # ore: amount of ore or "?" if unknown
        if ore != "?":
            # si le radar est détruit, il ne faut pas perdre notre connaissance
            # 0 => il n'y a plus d'ore
            # TODO : conserver la date de mise à jour pour aller creuser les cases les plus fraîches
            # print("To update cell", self, ore, hole, file=sys.stderr, flush=True)
            self.ore = int(ore)
        # hole: 1 if cell has a hole
        if self == Cell.get(15, 5):
            print("before:", self, file=sys.stderr, flush=True)
        if hole == "1":
            if self.has_hole is False:
                self.safe = False
            self.has_hole = True
        if self == Cell.get(15, 5):
            print("After:", self, file=sys.stderr, flush=True)

    def closest_adjacent(self, origin_cell):
        cells_with_ore.sort(key=lambda x: self.distance(x))
        if self.adjacents:
            self.adjacents.sort(key=lambda x: origin_cell.distance(x))
            return self.adjacents[0]
        else:
            return None

    def closest_base(self):
        return Cell.get(0, self.y)

    def standing_area(self):
        return Cell.get(6, self.y)

    def next_radar(self):
        """Renvoi la prochaine position pour le radar
        TODO : vérifier que l'enemi ne détruit pas nos radars"""
        Cell.NEXT_RADAR += 1
        return self.position_next_radar()

    def position_next_radar(self):
        index = Cell.NEXT_RADAR % len(Cell.COORD_RADARS)
        x, y = Cell.COORD_RADARS[index]
        return Cell.get(x, y)

    def next_mining_on_line(self):
        cell = self.right
        while cell.safe is False and cell.x <29:
            cell = cell.right
        return cell

    def next_bomb(self, radius=4, min_ore=3, cell_from=None):
        all_cells = [c for c in Cell.get_ore()]
        # print("With ore:", len(all_cells), file=sys.stderr, flush=True)
        cells_in_radius = [c for c in all_cells if self.distance(c) <= radius]
        # print("Within the radius:", len(cells_in_radius), file=sys.stderr, flush=True)
        with_min_ore = [c for c in cells_in_radius if c.ore >= min_ore]
        # print("With minimum ore:", len(with_min_ore), file=sys.stderr, flush=True)
        
        if with_min_ore:  # nothing match criterias
            cells = with_min_ore
        else:
            if cells_in_radius:
                cells = cells_in_radius
            else:
                if all_cells:
                    cells = all_cells
                else:
                    cells = Cell.CELLS
        
        if cell_from:  # we optimize move
            # return closest cell
            cells.sort(key=lambda c: cell_from.distance(c))
        
        return cells[0]

    def __str__(self):
        s = f"Cell({self.x}, {self.y})"
        if self.ore and self.ore > 0:
            s += f"o" * self.ore
        if self.has_bomb:
            s += "b"
        if self.has_hole:
            s += "h"
        if self.has_radar:
            s += "r"
        s+= "s" if self.safe else "u"
        return s

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    @classmethod
    def get(cls, x, y):
        if (x,y) not in cls.CELLS:
            cls.CELLS[(x,y)] = cls(x, y)
        return cls.CELLS[(x,y)]

    ORES = None
    CACHE_ORES = None
    @classmethod
    def get_ore(cls, min_ore=1):
        cells = cls.CELLS.values()
        cells = [c for c in cells if c.harvestable and c.ore >= min_ore]
        return cells
        # caching deactivated
        if not cls.CACHE_ORES or Entity.LOOP > cls.CACHE_ORES:
            cls.ORES = [_ for _ in cls.CELLS.values() 
                if _.ore > 0
                    and _.has_bomb is False]
            cls.CACHE_ORES = Entity.LOOP
        return cls.ORES


class Entity:
    ENTITIES = dict()
    DEBUG = True
    CPT_BOMBER = 5

    def __init__(self, id):
        self.id = id
        self.entity_type = None  # ROBOT, ENEMY, RADAR, BOMB
        self.item = None  # RADAR, BOMB, ORE
        self.current_cell = None
    
    def update_from_inputs(self, entity_type, x, y, item):
        # print("To update entity", self, entity_type, x, y, item, file=sys.stderr, flush=True)
        # entity_id: unique id of the entity
        # entity_type: 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
        # y: position of the entity
        # item: if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for BOMB, 4 for ORE)
        self.current_cell = Cell.get(x, y)
        # set type of entity
        if entity_type == 0:
            self.entity_type = "ROBOT"
        elif entity_type == 1:
            self.entity_type = "ENEMY"
        elif entity_type == 2:
            self.entity_type = "RADAR"
        else:
            self.entity_type = "BOMB"
        # set the item carried (if robot or enemy)
        self.item = None
        if item == 2:
            self.item = "RADAR"
        elif item == 3:
            self.item = "BOMB"
        elif item == 4:
            self.item = "ORE"

    def __str__(self):
        return f"{self.entity_type}({self.current_cell})"

    def _debug(self, *args):
        if Entity.DEBUG:
            print(*args, file=sys.stderr, flush=True)

    @classmethod
    def my_robots(cls):
        return [_ for _ in cls.ENTITIES.values() if _.entity_type == "ROBOT"]

    @classmethod
    def get(cls, id, entity_type=None):
        if id not in cls.ENTITIES:
            if entity_type == 0:  # it's one of my robots
                if cls.CPT_BOMBER > 0:
                    cls.ENTITIES[id] = RobotBomber(id)
                    cls.CPT_BOMBER -= 1
                else:
                    cls.ENTITIES[id] = Robot(id)
            else:
                cls.ENTITIES[id] = Entity(id)
        return cls.ENTITIES[id]


class Robot(Entity):
    ROBOTS = None
    RADAR_COOLDOWN = 0
    TRAP_COOLDOWN = 0

    @classmethod
    def get_robots(cls):
        """return all robots"""
        if not Robot.ROBOTS:
            Robot.ROBOTS = Entity.my_robots()
        return Robot.ROBOTS

    @classmethod
    def CPT_GET_RADAR(cls):
        robots = [r for r in cls.get_robots() if r.order == "GET_RADAR"]
        return len(robots)

    def __init__(self, id):
        super().__init__(id)
        self.order = None  # MINING, GET_RADAR
        self.order_cell = None  # cell where to do the action
        self.min_availabel_ore = None  # if order is mining, the amount of ore should be >=
    
    def is_dead(self):
        return self.current_cell.x == -1 and self.current_cell.y == -1

    def __str__(self):
        return f"ROBOT.{self.id}({self.current_cell}) {self.order}>{self.order_cell}"
    
    def compute_order(self):
        """If the robot doesn't have order
        - DELIVER: get back ore to the base (TODO)
        - SET_RADAR: go set a radar on the correct cell (TODO)
        - MINING: try to go mining on the closest ore
        - GET_RADAR: there is no mining available, go get a RADAR
        - STAND: go on standing column
        """
        print("compute for normal", file=sys.stderr, flush=True)
        if self.item is not None:
            if self.item == "ORE":
                self.set_order_deliver()
            elif self.item == "RADAR":
                self.set_order_set_radar()
            else:
                print("Error, harvest robot with BOMB?", self, file=sys.stderr, flush=True)
                self.set_order_mining()
        else:
            cell_with_ores = Cell.get_ore()
            nb_cell_with_ores = len(cell_with_ores) if cell_with_ores else 0
            # print("nb_cell_with_ores:", nb_cell_with_ores, file=sys.stderr, flush=True)
            
            # conditions to go get a radar
            cond1 = nb_cell_with_ores < 10  # no enough cells to harvest
            # print("No enough harvest:", cond1, file=sys.stderr, flush=True)
            cond2 = Robot.CPT_GET_RADAR() == 0  # no other robot are going
            cond3 = self.current_cell.x <= 2  # I am close to the base
            cond4 = Robot.RADAR_COOLDOWN == 0  # cooldown is cool
            # print("Cool_down is cool:", Robot.RADAR_COOLDOWN, cond4, file=sys.stderr, flush=True)
            
            if cond1 and cond2 and cond3 and cond4:
                self.set_order_get_radar()
            else:
                if nb_cell_with_ores > 0:
                    self.set_order_mining()
                else:
                    self.set_order_stand()
    
    def set_order_deliver(self):
        # robot is carrying an ORE; return to base to deliver
        self.order = "DELIVER"
        self.order_cell = self.current_cell.closest_base()
        self._debug(self)
    
    def set_order_set_radar(self):
        # Robot is carrying a radar; needs to go plant it
        self.order = "SET_RADAR"
        self.order_cell = self.current_cell.next_radar()
        self._debug(self)
    
    def set_order_mining(self):
        self.order = "MINING"
        self.order_cell = self.current_cell.closest_ore()
        self._debug(self)
    
    def set_order_get_radar(self):
        # go get a RADAR
        self.order = "GET_RADAR"
        Robot.RADAR_COOLDOWN = 5
        self.order_cell = self.current_cell.closest_base()
        self._debug(self)

    def set_order_stand(self):
        # Go to standing area
        self.order = "MINING"
        self.order_cell = Cell.get(max(4, self.current_cell.x + 1), self.current_cell.y)
        while self.order_cell.has_hole:
            self.order_cell = self.order_cell.right
        self._debug(self)
    
    def action(self):
        """Return the action according to the order
        . check if robot is dead to ignore it
        1. if current order => check it still possible
        2. if not order => compute new order
        3. transcode order to correct action to print
        """

        # Robot is dead ? Do noting
        if self.is_dead():
            return "MOVE 0 0 R.I.P."

        # if robot is idleing, it has nothing to do
        # or if the order can't be accomplished anymore (ie. mining an empty cell)
        # find another order
        if not self.order:
            self.compute_order()
        # check to avoid mistake
        if not self.order_cell:
            print("Error, il n'y a pas de order_cell", self, file=sys.stderr, flush=True)
            self.order = None  # cancel order badly configured
            return("WAIT")

        # move is not done and need to go further
        distance = self.current_cell.distance(self.order_cell)
        if self.order in ["MINING", "SET_RADAR", "SET_BOMB"]:
            if distance > 1:
                return self.move()
        else:
            if distance > 0:
                return self.move()

        # we are in position, let's do our work
        action = self.dispatch_action()
        # print("I will do", action, file=sys.stderr, flush=True)

        if action:
            return action
        else:
            print(f"Error, order={self.order} no action associated", file=sys.stderr, flush=True)
            return "WAIT"

    def dispatch_action(self):
        if self.order == "MINING":
            return self.mine()
        if self.order == "GET_RADAR":        
            return self.get_radar()
        if self.order == "SET_RADAR":
            return self.set_radar()
        if self.order == "DELIVER":
            return self.deliver()
        if self.order == "STAND":
            return self.stand()

    def move(self):
        return f"MOVE {self.order_cell.x} {self.order_cell.y}"

    def mine(self):
        # print(self.order_cell, file=sys.stderr, flush=True)
        if self.order_cell.has_bomb or self.order_cell.safe is False:
            self.order = None
            return "WAIT ooops"
        self.order_cell.ore -= 1
        self.order_cell.has_hole = True
        return f"DIG {self.order_cell.x} {self.order_cell.y} my ore!"

    def set_radar(self):
        self.order_cell.has_hole = True
        return f"DIG {self.order_cell.x} {self.order_cell.y} hey oh cap'tain, new vision here"

    def get_radar(self):
        return "REQUEST RADAR"

    def stand(self):
        return "WAIT"

    def deliver(self):
        # quick move to most recent radar
        cell = self.current_cell.position_next_radar()
        return f"MOVE {cell.x} {cell.y} my preciiious"

    def complete_order(self):
        if self.order == "MINING":
            self.complete_mining()
        elif self.order == "GET_RADAR":
            self.complete_get_radar()
        elif self.order == "SET_RADAR":
            self.complete_set_radar()
        elif self.order == "STAND":
            self.complete_stand()
        elif self.order == "DELIVER":
            self.complete_deliver()
        else:
            print(f"Error, no complete for={self.order}", file=sys.stderr, flush=True)
            self.order = None
    
    def complete_mining(self):
        # I carry ORE or there is no ORE to harvest on my target
        if self.item == "ORE" or self.order_cell.ore == 0:
            self.order = None  # order completed
        # there is a bomb on my targeted cell
        if self.order_cell.has_bomb:
            self.order = None
        # target is not sage
        if self.order_cell.safe is False:
            self.order = None
        # not enough ore for all the miners
        miners = [r for r in Robot.get_robots()
            if r.order == "MINING" and r.order_cell == self.order_cell]
        if len(miners) > self.order_cell.ore:
            self.order = None

    def complete_get_radar(self):
        if self.item == "RADAR":
            self.order = None

    def complete_set_radar(self):
        if self.item != "RADAR":
            self.order = None

    def complete_deliver(self):
        if self.item != "ORE":
            self.order = None

    def complete_stand(self):
        self.order = None

class RobotBomber(Robot):

    @classmethod
    def CPT_GET_BOMB(cls):
        robots = [r for r in cls.get_robots() if r.order == "GET_BOMB"]
        return len(robots)


    def __init__(self, id):
        """radar_pos = (x, y)"""
        # print(f"Init bomber", file=sys.stderr, flush=True)
        super().__init__(id)
        self.bomb_planted = 0

    def set_order_get_bomb(self):
        self.order = "GET_BOMB"
        self.order_cell = self.current_cell.closest_base()
        self._debug(self)

    def set_order_set_bomb(self):
        self.order = "SET_BOMB"
        self.order_cell = self.current_cell.closest_ore(min_ore=2)
        if not self.order_cell:
            self.order_cell = self.current_cell.closest_ore()
        if self.order_cell:
            self.order_cell.has_bomb = True
            self._debug(self)
        else:
            self.set_order_stand()

    def compute_order(self):
        print("compute for bomber", file=sys.stderr, flush=True)
        # I have planted enough bombs
        # I should behave like a simple robot
        if self.bomb_planted > 5:
            return super().compute_order()

        cell_with_ores = Cell.get_ore()
        nb_cell_with_ores = len(cell_with_ores) if cell_with_ores else 0
        
        # We need more bomb, niark niark niark
        # I carry nothing then I should plant my radar or a bomb
        # conditions to go get a bomb
        cond1 = nb_cell_with_ores > 0  # at least one cell is interesting enemy
        cond2 = RobotBomber.CPT_GET_BOMB() == 0  # no other robot are going
        cond3 = self.current_cell.x <= 2  # I am close to the base
        cond4 = self.item is None  # do not carry anything
        cond5 = Robot.TRAP_COOLDOWN == 0  # cooldown is cool

        if self.item == "BOMB":
            self.set_order_set_bomb()
        elif cond1 and cond2 and cond3 and cond4 and cond5:
            self.set_order_get_bomb() 
        else:
            # get order for a normal robot
            super().compute_order()

    def dispatch_action(self):
        if self.order == "GET_BOMB":
            return self.get_bomb()
        elif self.order == "SET_BOMB":
            return self.set_bomb()
        else:
            return super().dispatch_action()

    def get_bomb(self):
        return "REQUEST TRAP **whistle**"
    
    def set_bomb(self):
        self.bomb_planted += 1
        self.order_cell.has_bomb = True
        self.order_cell.has_hole = True
        return f"DIG {self.order_cell.x} {self.order_cell.y} boom"

    def complete_order(self):
        if self.order == "GET_BOMB":
            self.complete_get_bomb()
        elif self.order == "SET_BOMB":
            self.complete_set_bomb()
        else:
            super().complete_order()

    def complete_set_bomb(self):
        if self.item != "BOMB":
            self.order = None

    def complete_get_bomb(self):
        if self.item == "BOMB":
            self.order = None

# game loop
Entity.LOOP = 0
while True:
    Entity.LOOP += 1
    # my_score: Amount of ore delivered
    my_score, opponent_score = [int(i) for i in input().split()]
    for y in range(height):
        inputs = input().split()
        for x in range(width):
            Cell.get(x, y).update_from_input(inputs)

    # entity_count: number of entities visible to you
    # Robot.RADAR_COOLDOWN: turns left until a new radar can be requested
    # trap_cooldown: turns left until a new trap can be requested
    entity_count, Robot.RADAR_COOLDOWN, trap_cooldown = [int(i) for i in input().split()]
    for i in range(entity_count):
        # entity_id: unique id of the entity
        # entity_type: 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
        # y: position of the entity
        # item: if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for TRAP, 4 for ORE)
        entity_id, entity_type, x, y, item = [int(j) for j in input().split()]
        Entity.get(entity_id, entity_type).update_from_inputs(**{
            "entity_type": entity_type,
            "x": x,
            "y": y,
            "item": item,
        })
    # check if order from previous loop are still going
    for my_robot in Entity.my_robots():
        my_robot.complete_order()

    for my_robot in Entity.my_robots():

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr, flush=True)

        # WAIT|MOVE x y|DIG x y|REQUEST item
        print(my_robot.action())
