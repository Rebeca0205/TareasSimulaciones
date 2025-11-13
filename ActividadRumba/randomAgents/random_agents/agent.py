from mesa.discrete_space import CellAgent, FixedAgent

class RandomAgent(CellAgent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID
    """
    def __init__(self, model, cell, energy=100):
        """
        Creates a new random agent.
        Args:
            model: Model reference for the agent
            cell: Reference to its position within the grid
        """
        super().__init__(model)
        self.cell = cell
        self.energy = energy

    def clean(self):
        """If possible, eat grass at current location."""
        dirt_patch = next(
            obj for obj in self.cell.agents if isinstance(obj, DirtPatch)
        )
        if dirt_patch:
            dirt_patch = False

    def move(self):
        """
        Determines the next empty cell in its neighborhood, and moves to it
        """
        if self.random.random() < 0.5:
            # Checks which grid cells are empty
            next_moves = self.cell.neighborhood.select(lambda cell: cell.is_empty)
            self.cell = next_moves.select_random_cell()

    def step(self):
        """
        Determines the new direction it will take, and then moves
        """
        self.move()
        self.energy -= 1 
        self.clean()

        # Handle death and reproduction
        if self.energy < 0:
            self.remove()


class ObstacleAgent(FixedAgent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell=cell

    def step(self):
        pass

class DirtPatch(FixedAgent):
    """
    A dirt patch that appears at a fixed rate and can be cleaned by the roomba.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell=cell
        self.is_dirt = True

class ChargingCell(FixedAgent):
    """
    A charging station that appears at a fixed rate and can be used by the roomba to charge its energy.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell=cell