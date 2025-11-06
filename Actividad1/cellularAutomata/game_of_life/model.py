from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import Cell


class ConwaysGameOfLife(Model):
    """Represents the 2-dimensional array of cells in Conway's Game of Life."""

    def __init__(self, width=50, height=50, initial_fraction_alive=0.2, seed=None):
        """Create a new playing area of (width, height) cells."""
        super().__init__(seed=seed)

        """Grid where cells are connected to their 8 neighbors.

        Example for two dimensions:
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1),
        ]
        """
        self.grid = OrthogonalMooreGrid((width, height), capacity=1, torus=True)

        self.cell_grid = {}

        self.current_row = height - 1

        # Place a cell at each location, with some initialized to
        # ALIVE and some to DEAD.
        for cell in self.grid.all_cells:
            x, y = cell.coordinate
            init_state=(
                Cell.ALIVE
                if (y == self.current_row and self.random.random() < initial_fraction_alive)
                else Cell.DEAD
            )
            self.cell_grid[(x, y)] = Cell(
                self,
                cell,
                init_state=init_state,   
            )

        self.running = True

    def step(self):
        """Perform the model step in two stages:

        - First, all cells assume their next state (whether they will be dead or alive)
        - Then, all cells change state to their next state.
        """
        width = self.grid.width

        if self.current_row <= 0:
            self.running = False
            return
        

        prev_row = self.current_row #fila actual
        next_row = prev_row -1 #fila actualizada

        for x in range(width):
            #posiciones de los neighbors en la misma fila
            left_pos = ((x - 1) % width, prev_row)
            center_pos = (x, prev_row)
            right_pos = ((x + 1) % width, prev_row)

            #guardadr posiciones de agentes
            left_agent = self.cell_grid[left_pos]
            center_agent = self.cell_grid[center_pos]
            right_agent = self.cell_grid[right_pos]

            #actualizar la posicion hacia abajo
            next_pos = (x, next_row)
            next_agent = self.cell_grid[next_pos]

            #Comparacion de agentes muertos y vivos
            next_agent.set_next_state(
                left_agent.state,
                center_agent.state,
                right_agent.state
            )

        #Mover a siguiente fila
        for x in range(width):
            next_agent = self.cell_grid[(x, next_row)]
            next_agent.assume_state()

        self.current_row = next_row
