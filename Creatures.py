### COMPSCI 130, Summer School 2019
### Project Two - Creatures
import turtle
import hashlib
from collections import Counter


class Creature:
    """This class represents a creature"""

    def __init__(self, row, col, dna, direction):
        """Creates a creature at the given row/col position."""
        self.direction = direction
        self.row = row
        self.col = col
        self.dna = dna
        self.next_instruction = 1
        self.ahead = None
        self.name = self.get_species()

    def __str__(self):
        """Returns a string representation of this creature."""
        return f'{self.get_species()} {self.row} {self.col} {self.direction}'

    def draw(self, grid_size, top_left_x, top_left_y):
        """Draws this creature in the colour specified in it's dna.

        The size of the grid squares, and the position of the top-left pixel
        are provided as input.
        """

        # Compute the position of the top left corner of the cell this
        # creature is in
        x = top_left_x + (self.col - 1) * grid_size
        y = top_left_y - (self.row - 1) * grid_size

        # Draw the creature

        # Overwrite everything in the cell
        turtle.goto(x, y)
        turtle.pendown()
        turtle.begin_fill()
        turtle.color("white")
        turtle.goto(x + grid_size, y)
        turtle.goto(x + grid_size, y - grid_size)
        turtle.goto(x, y - grid_size)
        turtle.goto(x, y)  # This one is redundant
        turtle.end_fill()
        turtle.penup()

        turtle.color(self.dna[0].split(":")[1])

        # Draw a triangle in the direction this creature is facing
        if self.direction == 'North':
            turtle.goto(x + (grid_size / 2), y)
            turtle.pendown()
            turtle.begin_fill()
            turtle.goto(x, y - grid_size)
            turtle.goto(x + grid_size, y - grid_size)

        elif self.direction == 'East':
            turtle.goto(x + grid_size, y - (grid_size / 2))
            turtle.pendown()
            turtle.begin_fill()
            turtle.goto(x, y)
            turtle.goto(x, y - grid_size)

        elif self.direction == 'South':
            turtle.goto(x + (grid_size / 2), y - grid_size)
            turtle.pendown()
            turtle.begin_fill()
            turtle.goto(x, y)
            turtle.goto(x + grid_size, y)

        else:  # West
            turtle.goto(x, y - (grid_size / 2))
            turtle.pendown()
            turtle.begin_fill()
            turtle.goto(x + grid_size, y)
            turtle.goto(x + grid_size, y - grid_size)

        turtle.end_fill()
        turtle.penup()

        turtle.color("black")

    def get_species(self):
        """Returns the name of the species for this creature."""
        return self.dna[0].split(":")[0]

    def get_position(self):
        """Returns the current position of this creature."""
        return self.row, self.col

    def get_ahead_pos(self):
        """Returns the position ahead of this creature."""
        ahead_row = self.row
        ahead_col = self.col
        if self.direction == 'North':
            ahead_row = ahead_row - 1
        elif self.direction == 'South':
            ahead_row = ahead_row + 1
        elif self.direction == 'East':
            ahead_col = ahead_col + 1
        elif self.direction == 'West':
            ahead_col = ahead_col - 1
        return ahead_row, ahead_col

    def op_go(self, op):
        """Sets the next instruction to the argument of op."""
        self.next_instruction = int(op[1])

    def op_hop(self, row, col):
        """Moves this creature to the given position if the position is empty.
        """
        if self.ahead == 'EMPTY':
            self.row = row
            self.col = col

    def op_reverse(self):
        """Reverses this creature's direction."""
        if self.direction == 'North':
            self.direction = 'South'
        elif self.direction == 'South':
            self.direction = 'North'
        elif self.direction == 'East':
            self.direction = 'West'
        elif self.direction == 'West':
            self.direction = 'East'

    def op_ifnotwall(self, op):
        """Sets the next instruction to the argument of op if the position
        ahead of this creature is empty.
        """
        if self.ahead == 'EMPTY':
            self.next_instruction = int(op[1])
        else:
            self.next_instruction += 1

    def op_twist(self):
        """Turns this creature 90 degrees clockwise."""
        if self.direction == 'North':
            self.direction = 'East'
        elif self.direction == 'East':
            self.direction = 'South'
        elif self.direction == 'South':
            self.direction = 'West'
        elif self.direction == 'West':
            self.direction = 'North'

    def op_ifsame(self, op):
        """Sets the next instruction to the argument of op if the position
        ahead of this creature contains a creature of the same species,
        otherwise the instruction immediately after this op is run.
        """
        if isinstance(self, type(self.ahead)) and self.name == self.ahead.name:
            self.next_instruction = int(op[1])
        else:
            self.next_instruction += 1

    def op_ifenemy(self, op):
        """Sets the next instruction to the argument of op if the position
        ahead of this creature contains a creature of a different species,
        otherwise the instruction immediately after this op is run.
        """
        if isinstance(self, type(self.ahead)) and self.name != self.ahead.name:
            self.next_instruction = int(op[1])
        else:
            self.next_instruction += 1

    def op_ifrandom(self, op, world):
        """Sets the next instruction to the argument of op approx. 50% of
        the time, otherwise the instruction immediately after this op is run.
        """
        if world.pseudo_random():
            self.next_instruction = int(op[1])
        else:
            self.next_instruction += 1

    def op_infect(self):
        """If the cell immediately in front of this creature contains another
        creature of a different species then this instruction will infect that
        other creature.

        When a creature is infected, it keeps its position and direction, but
        its DNA (i.e. its list of instructions) are replaced with those of the
        infecting creature.
        """
        if isinstance(self, type(self.ahead)) and self.name != self.ahead.name:
            self.ahead.name = self.name
            self.ahead.dna = self.dna

    def make_move(self, world):
        """Execute a single non-control-flow instruction for this creature by
        following the instructions in its dna.

        non-control-flow instructions are instructions which do not end this
        creatures turn.
        """
        finished = False
        ahead_row, ahead_col = self.get_ahead_pos()
        self.ahead = world.get_cell(ahead_row, ahead_col)

        dispatch = {
            'go': self.op_go,
            'hop': self.op_hop,
            'reverse': self.op_reverse,
            'ifnotwall': self.op_ifnotwall,
            'twist': self.op_twist,
            'ifsame': self.op_ifsame,
            'ifenemy': self.op_ifenemy,
            'ifrandom': self.op_ifrandom,
            'infect': self.op_infect
        }

        # Operations that do not end a creature's turn
        control_flow_ops = set(
            ['go', 'ifnotwall', 'ifsame', 'ifenemy', 'ifrandom'])

        # Execute instructions until a non-control-flow op is run
        while not finished:
            next_op = self.dna[self.next_instruction]
            op = next_op.split()

            op_args = {
                'go': {
                    'op': op
                },
                'hop': {
                    'row': ahead_row,
                    'col': ahead_col
                },
                'ifnotwall': {
                    'op': op
                },
                'ifsame': {
                    'op': op
                },
                'ifenemy': {
                    'op': op
                },
                'ifrandom': {
                    'op': op,
                    'world': world
                },
            }

            try:
                dispatch[op[0]](**op_args.get(op[0], {}))
            except KeyError:
                raise ValueError(f"can't find instruction '{next_op}'.")

            if op[0] in control_flow_ops:
                continue

            self.next_instruction += 1
            finished = True


class World:
    """This class represents the grid-based world."""

    def __init__(self, size, max_generations):
        """Creates a new world with the given grid-size and number of generations.
        """
        self.size = size
        self.generation = 0
        self.max_generations = max_generations
        self.creatures = []

    def add_creature(self, c):
        """Adds a creature to the world."""
        self.creatures.append(c)

    def get_cell(self, row, col):
        """Gets the contents of the specified cell.

        Returns:
            'WALL': if the cell is off the grid
            creature: if the cell contains a creature the creature is returned
            'EMPTY': if the cell isn't a wall or creature
        """
        if (row <= 0 or col <= 0 or row >= self.size + 1
                or col >= self.size + 1):
            return 'WALL'

        # Check if there are any creatures in this world at the given position
        for creature in self.creatures:
            if creature.row == row and creature.col == col:
                return creature

        return 'EMPTY'

    def simulate(self):
        """Executes one generation for the world by allowing each creature in
        this world to make a move in the order they were added to this world.

        If there are no more generations to simulate, the world is printed.
        """
        if self.generation < self.max_generations:
            self.generation += 1
            for creature in self.creatures:
                creature.make_move(self)
            return False
        else:
            print(self)
            return True

    def __str__(self):
        """Returns a string representation of the world."""

        # Count the frequency of each creature
        counts = Counter([c.name for c in self.creatures]).most_common()

        # Sort in descending order by frequency, and then alphabetically
        counts.sort(key=lambda x: (-x[1], x[0]))

        # Convert each creature to it's string representation
        creatures = [c.__str__() for c in self.creatures]

        return f'{self.size}\n' + f'{counts}\n' + '\n'.join(creatures)

    def draw(self):
        """Displays the world by drawing each creature and in this world and
        the world's grid.
        """

        # Basic coordinates of grid within 800x800 window
        # - total width and position of top left corner
        grid_width = 700
        top_left_x = -350
        top_left_y = 350
        grid_size = grid_width / self.size

        # Draw the creature
        for creature in self.creatures:
            creature.draw(grid_size, top_left_x, top_left_y)

        # Draw the bounding box
        turtle.goto(top_left_x, top_left_y)
        turtle.setheading(0)
        turtle.pendown()
        for i in range(0, 4):
            turtle.rt(90)
            turtle.forward(grid_width)
        turtle.penup()

        # Draw rows
        for i in range(self.size):
            turtle.setheading(90)
            turtle.goto(top_left_x, top_left_y - grid_size * i)
            turtle.pendown()
            turtle.forward(grid_width)
            turtle.penup()

        # Draw columns
        for i in range(self.size):
            turtle.setheading(180)
            turtle.goto(top_left_x + grid_size * i, top_left_y)
            turtle.pendown()
            turtle.forward(grid_width)
            turtle.penup()

    def pseudo_random(self):
        """Returns a 0 or 1 based on the current world state."""
        total = sum(c.row + c.col for c in self.creatures) * self.generation
        return int(hashlib.sha256(str(total).encode()).hexdigest(), 16) % 2


class CreatureWorld:
    """This class reads the data files from disk and sets up the window."""

    def __init__(self):
        """Initialises the window, and registers the begin_simulation function
        to be called when the space-bar is pressed.
        """
        self.framework = SimulationFramework(800, 800,
                                             'COMPSCI 130 Project Two')
        self.framework.add_key_action(self.begin_simulation, ' ')
        self.framework.add_tick_action(
            self.next_turn,
            100)  # Delay between animation "ticks" - smaller is faster.

    def begin_simulation(self):
        """Starts the animation."""
        self.framework.start_simulation()

    def end_simulation(self):
        """Ends the animation."""
        self.framework.stop_simulation()

    def setup_simulation(self):
        """Reads the data files from disk."""

        # If new creatures are defined, they should be added to this list
        all_creatures = [
            'Hopper', 'Parry', 'Rook', 'Roomber', 'Randy', 'Flytrap'
        ]

        # Read the creature location data
        with open('world_input.txt') as f:
            world_data = f.read().splitlines()

        # Read the dna data for each creature type
        dna_dict = {}
        for creature in all_creatures:
            with open('Creatures//' + creature + '.txt') as f:
                dna_dict[creature] = f.read().splitlines()

        # Create a world of the specified size, and set the number of
        # generations to be performed when the simulation runs
        world_size = world_data[0]
        world_generations = world_data[1]
        self.world = World(int(world_size), int(world_generations))

        for creature in world_data[2:]:
            data = creature.split()
            dna = dna_dict[data[0]]
            row = int(data[1])
            col = int(data[2])
            direction = data[3]

            if self.world.get_cell(row, col) == 'EMPTY':
                self.world.add_creature(Creature(row, col, dna, direction))

        # Draw the initial layout of the world
        self.world.draw()

    def next_turn(self):
        """This function is called each time the animation loop "ticks". The
        screen should be redrawn each time.
        """
        turtle.clear()
        self.world.draw()
        if self.world.simulate():
            self.end_simulation()

    def start(self):
        """This function sets up the simulation and starts the animation loop.
        """
        self.setup_simulation()
        turtle.mainloop()  # Must appear last.


class SimulationFramework:
    """This is the simulation framework - it does not need to be edited."""

    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.simulation_running = False
        self.tick = None  # function to call for each animation cycle
        self.delay = 100  # default is .1 second.
        turtle.title(title)  # title for the window
        turtle.setup(width, height)  # set window display
        turtle.hideturtle()  # prevent turtle appearance
        turtle.tracer(False)  # prevent turtle animation
        turtle.listen()  # set window focus to the turtle window
        turtle.mode('logo')  # set 0 direction as straight up
        turtle.penup()  # don't draw anything
        self.__animation_loop()

    def start_simulation(self):
        self.simulation_running = True

    def stop_simulation(self):
        self.simulation_running = False

    def add_key_action(self, func, key):
        turtle.onkeypress(func, key)

    def add_tick_action(self, func, delay):
        self.tick = func
        self.delay = delay

    def __animation_loop(self):
        if self.simulation_running:
            self.tick()
        turtle.ontimer(self.__animation_loop, self.delay)


cw = CreatureWorld()
cw.start()
