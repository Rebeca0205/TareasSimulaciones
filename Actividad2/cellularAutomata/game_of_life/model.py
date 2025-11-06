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
                if (self.random.random() < initial_fraction_alive)
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
        height = self.grid.height

        for agent in self.agents:
            #posicion del agente
            x, y = agent.pos

            #posiciones de los neighbors en la misma fila
            arriba = (y + 1) % height # este es e valor y arriba del agente actual
            left_pos = ((x - 1) % width, arriba)
            center_pos = (x, arriba)
            right_pos = ((x + 1) % width, arriba)

            #guardar estados de agentes de cada posicion
            left_state = self.cell_grid[left_pos].state
            center_state = self.cell_grid[center_pos].state
            right_state = self.cell_grid[right_pos].state

            #Usa la funcion de agent para determinar el siguiente estdo
            agent.set_next_state(left_state, center_state, right_state)

            #Mover a siguiente fila
        for a in self.agents:
            a.assume_state()
