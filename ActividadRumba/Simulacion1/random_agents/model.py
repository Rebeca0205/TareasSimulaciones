from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from mesa.datacollection import DataCollector

from .agent import RandomAgent, ObstacleAgent, DirtPatch, ChargingCell

class RandomModel(Model):
    """
    Creates a new model with random agents.
    Args:
        num_agents: Number of agents in the simulation
        height, width: The size of the grid to model
    """
    def __init__(self, num_agents=1, num_obstacle = 50, dirt = 200, charge = 5, width=8, height=8, seed=42):

        super().__init__(seed=seed)
        self.num_agents = num_agents
        self.num_obstacle = num_obstacle
        self.dirt = dirt
        self.charge = charge
        self.seed = seed
        self.width = width
        self.height = height

        self.grid = OrthogonalMooreGrid([width, height], torus=False)
        self.datacollector = DataCollector(
            model_reporters={
                "Suciedad": lambda m: len(m.agents_by_type[DirtPatch]),
                "Energy": lambda m: next(
                    a.energy for a in m.agents if isinstance(a, RandomAgent)
                ),
            },
            agent_reporters={
                "Energy": lambda a: a.energy if isinstance(a, RandomAgent) else None,
            }
        )

        # Identify the coordinates of the border of the grid
        border = [(x,y)
                  for y in range(height)
                  for x in range(width)
                  if y in [0, height-1] or x in [0, width - 1]]

        # Create the border cells
        for _, cell in enumerate(self.grid):
            if cell.coordinate in border:
                ObstacleAgent(self, cell=cell)
        
        ObstacleAgent.create_agents(
            self,
            self.num_obstacle,
            cell=self.random.choices(self.grid.empties.cells, k=self.num_obstacle)
        )

        DirtPatch.create_agents(
            self,
            self.dirt,
            cell=self.random.choices(self.grid.empties.cells, k=self.dirt)
        )

        cell = self.grid[1, 1]
        ChargingCell(self, cell=cell)
        RandomAgent(self, cell=cell)

        self.running = True

    def step(self):
        '''Advance the model by one step.'''
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)
