# FixedAgent: Immobile agents permanently fixed to cells
from mesa.discrete_space import FixedAgent

class Cell(FixedAgent):
    """Represents a single ALIVE or DEAD cell in the simulation."""

    DEAD = 0
    ALIVE = 1

    @property
    def x(self):
        return self.cell.coordinate[0]

    @property
    def y(self):
        return self.cell.coordinate[1]

    @property
    def is_alive(self):
        return self.state == self.ALIVE

    @property
    def neighbors(self):
        return self.cell.neighborhood.agents
    
    def __init__(self, model, cell, init_state=DEAD):
        """Create a cell, in the given state, at the given x, y position."""
        super().__init__(model)
        self.cell = cell
        self.pos = cell.coordinate
        self.state = init_state
        self._next_state = None

    def determine_state(self):
        """Compute if the cell will be dead or alive at the next tick.  This is
        based on the number of alive or dead neighbors.  The state is not
        changed here, but is just computed and stored in self._nextState,
        because our current state may still be necessary for our neighbors
        to calculate their next state.
        """
        # Get the neighbors and apply the rules on whether to be alive or dead
        # at the next tick.
        live_neighbors = 0
        for n in self.neighbors:
            live_neighbors += n.is_alive

        # Assume nextState is unchanged, unless changed below.
        self.next_state = self.state

    def set_next_state(self, left_state, center_state, right_state):
        a = 1 if left_state == self.ALIVE else 0 
        b = 1 if center_state == self.ALIVE else 0
        c = 1 if right_state == self.ALIVE else 0
        pattern = f"{a}{b}{c}"

        if pattern in ("111", "101", "010", "000"):
            self.next_state = self.DEAD
        else:
            self.next_state = self.ALIVE

        self.state = self.next_state
        self.next_state = None

    def assume_state(self):
        """Set the state to the new computed state -- computed in step()."""
        if self.next_state is not None:
            self.state = self.next_state
            self.next_state = None
