from mesa.discrete_space import CellAgent, FixedAgent
from collections import deque

class RandomAgent(CellAgent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID
    """
    def __init__(self, model, cell, energy=100, charging = False):
        """
        Creates a new random agent.
        Args:
            model: Model reference for the agent
            cell: Reference to its position within the grid
        """
        super().__init__(model)
        self.cell = cell
        self.energy = energy
        self.movements = 0
        self.max_energy = 100
        self.low_battery = 40 
        self.charging = charging

        self.charger_coord = self.cell.coordinate  # (x, y)
        self.known_chargers = set(self.charger_coord)   #Necesario para mas de un roomba
        
        self.visit_count = {}      # (x, y) , veces visitada
        self.last_coordinate = self.cell.coordinate 
        self.path_to_charger = []
        self.return_stack = []          # Pila para regresar del cargador
        self.going_to_charger = False 
        self.just_finished_charging = False

    def _register_visit(self):
        """Registrar la celda actual como visitada."""
        coord = self.cell.coordinate
        self.visit_count[coord] = self.visit_count.get(coord, 0) + 1
        self.last_coordinate = coord

    def _neighbor_cells_with(self, AgentType):
        """Celdas vecinas que contienen al menos un agente de tipo AgentType."""
        return self.cell.neighborhood.select(
            lambda c: any(isinstance(obj, AgentType) for obj in c.agents)
        )

    def _neighbors_no_obstacle(self, cell):
        """Vecinos ortogonales sin obstáculos."""
        x, y = cell.coordinate
        neighbors = []

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            try:
                ncell = self.model.grid[nx, ny]
            except Exception:
                continue

            has_obstacle = any(isinstance(obj, ObstacleAgent) for obj in ncell.agents)
            if not has_obstacle:
                neighbors.append(ncell)

        return neighbors
    
    def _pick_unvisited_neighbor(self):
        """
        Regresa una celda vecina no visitada (sin obstáculos) o None si no hay.
        """
        neighbors = self._neighbors_no_obstacle(self.cell)
        if not neighbors:
            return None

        unvisited = [
            c for c in neighbors
            if self.visit_count.get(c.coordinate, 0) == 0
        ]

        if not unvisited:
            return None

        return self.model.random.choice(unvisited)
    
    def _bfs_path(self, goal_coord=None, goal_condition=None):
        """
        BFS genérico que devuelve un camino (lista de celdas) desde la celda actual
        hasta:
        - goal_coord (si se da), o
        - la primera celda que cumpla goal_condition(coord).

        Si no hay camino, devuelve [].
        """
        start = self.cell
        start_coord = start.coordinate

        queue = deque([start])
        came_from = {start_coord: None}
        found_coord = None

        while queue:
            current = queue.popleft()
            ccoord = current.coordinate

            # Caso 1: buscamos una coordenada específica
            if goal_coord is not None and ccoord == goal_coord:
                found_coord = ccoord
                break

            # Caso 2: buscamos la primera celda que cumpla una condición
            if (
                goal_coord is None
                and goal_condition is not None
                and ccoord != start_coord
                and goal_condition(ccoord)
            ):
                found_coord = ccoord
                break

            for neighbor in self._neighbors_no_obstacle(current):
                ncoord = neighbor.coordinate
                if ncoord not in came_from:
                    came_from[ncoord] = ccoord
                    queue.append(neighbor)

        if found_coord is None:
            return []

        # Reconstruir el camino desde found_coord -> start
        path_coords = []
        current_coord = found_coord
        while current_coord != start_coord:
            path_coords.append(current_coord)
            current_coord = came_from[current_coord]

        path_coords.reverse()  # de start a objetivo
        return [self.model.grid[x, y] for (x, y) in path_coords]

    def _follow_path(self, path):
        """Avanza un paso siguiendo el path (cada celda es vecina)."""
        if not path:
            return
        
        # Solo miramos la siguiente celda (decisión local)
        next_cell = path[0]

        # ¿Hay una estación de carga en esa celda?
        has_charger = any(isinstance(obj, ChargingCell) for obj in next_cell.agents)
        # ¿Hay otro roomba ya parado ahí?
        has_other_roomba = any(
            isinstance(obj, RandomAgent) and obj is not self
            for obj in next_cell.agents
        )

        # Si la siguiente celda ES un cargador y ya está ocupada, no entramos
        if has_charger and has_other_roomba:
            # Borrar ruta actual y el agente pueda recalcular otra ruta a otro cargador
            self.path_to_charger = []
            return
        
        if self.going_to_charger:
            # Guardamos la coordenada de donde ESTÁ antes de moverse
            self.return_stack.append(self.cell.coordinate)

        next_cell = path.pop(0)
        self.cell = next_cell

    def clean(self):
        """If possible, clean at current location."""
        dirt_patches = [obj for obj in self.cell.agents if isinstance(obj, DirtPatch)]
        for dirt in dirt_patches:
            dirt.remove()

    def _charge_if_on_station(self):
        self.energy += 5

        # Si ya está lleno, dejar de "estar cargando"
        if self.energy >= self.max_energy:
            self.charging = False
            self.just_finished_charging = True 
    
    def _neighbors_no_obstacle(self, cell):
        x, y = cell.coordinate
        neighbors = []

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:  # 4 direcciones
            nx, ny = x + dx, y + dy
            # evitar salir del grid
            try:
                ncell = self.model.grid[nx, ny]
            except Exception:
                continue

            has_obstacle = any(isinstance(obj, ObstacleAgent) for obj in ncell.agents)
            if not has_obstacle:
                neighbors.append(ncell)

        return neighbors
    
    def _see_chargers_in_neighborhood(self):
        """
        Revisa la celda actual y las vecinas.
        Si encuentra estaciones de carga, guarda sus coordenadas en known_chargers.
        """
        # Incluir la celda actual
        if any(isinstance(obj, ChargingCell) for obj in self.cell.agents):
            self.known_chargers.add(self.cell.coordinate)

        # Incluir vecinos que tengan cargador
        neighbor_chargers = self._neighbor_cells_with(ChargingCell)
        for c in neighbor_chargers:
            self.known_chargers.add(c.coordinate)

    def _explore_step(self):
        """
        Movimiento de exploración:
        1. Si hay vecinos nunca visitados, ir a uno de ellos.
        2. Si no hay vecinos no visitados, intentar retroceder a la celda anterior
           (last_coordinate) si es vecina.
        3. Si tampoco se puede, ir al vecino menos visitado.
        """
        neighbors = self._neighbors_no_obstacle(self.cell)
        if not neighbors:
            return

        target = self._pick_unvisited_neighbor()
        if target is not None:
            self.cell = target
            return

        # Si no hay no visitados, ir a menos visitado
        visit_pairs = [
            (c, self.visit_count.get(c.coordinate, 0))
            for c in neighbors
        ]
        min_visits = min(v for (_, v) in visit_pairs)
        best = [c for (c, v) in visit_pairs if v == min_visits]

        self.cell = self.model.random.choice(best)
            

    def moveToCharger(self):
        """
        Se mueve hacia la estación de carga (celda inicial) usando BFS.
        """
        # Ver si hay cargadores cerca y actualizarlos en la memoria
        self._see_chargers_in_neighborhood()

        # Si ya está sobre un cargador, empezar a cargar
        if any(isinstance(obj, ChargingCell) for obj in self.cell.agents):
            self.charging = True
            self.just_finished_charging = False  
            self.going_to_charger = False   # Ya llegó
            self.path_to_charger = []
            return

        # Asegurarnos de que por lo menos conozca su cargador inicial
        if not self.known_chargers:
            self.known_chargers.add(self.charger_coord)

        self.going_to_charger = True

        # Usar BFS para encontrar el camino más corto
        # a cualquiera de los cargadores conocidos
        self.path_to_charger = self._bfs_path(
            goal_coord=None,
            goal_condition=lambda coord: coord in self.known_chargers
        )

        # Si por alguna razón no encontró camino, intentar al cargador inicial directo
        if not self.path_to_charger:
            self.path_to_charger = self._bfs_path(goal_coord=self.charger_coord)
            if not self.path_to_charger:
                # No hay forma de llegar a ningún cargador
                return
        
        self._follow_path(self.path_to_charger)

    def move_with_return_stack(self):
        coord = self.return_stack.pop()   # última celda donde estuvo
        x, y = coord
        self.cell = self.model.grid[x, y]

    def move(self):
        """
        Si hay suciedad en vecinos, se acerca a ella.
        Si no hay, explora.
        """

        self._see_chargers_in_neighborhood()

        neighbor_dirt_cells = self._neighbor_cells_with(DirtPatch)

        if len(neighbor_dirt_cells) == 0:
            self._explore_step()
            return

        # elegir una celda con suciedad (todas están a distancia 1)
        target = neighbor_dirt_cells.select_random_cell()
        self.cell = target


    def step(self):

        # Limpiar si hay suciedad en la celda actual
        if [obj for obj in self.cell.agents if isinstance(obj, DirtPatch)]:
            self.clean()
            self.energy -= 1

        # Si se queda sin energía, muere
        if self.energy <= 0:
            if any(isinstance(obj, ChargingCell) for obj in self.cell.agents):
                self.charging = True
                self._charge_if_on_station()
                self._register_visit()
            # Si no está en un cargador, se queda "muerto" ahí, sin moverse
            return

        # Cargar si tiene estado de cargando y esta encima de un cargador
        if self.charging and any(isinstance(obj, ChargingCell) for obj in self.cell.agents):
            self._charge_if_on_station()
            self._register_visit()
            # OJO: si SIGUE cargando, sí nos salimos
            if self.charging:
                return

        # Ir al cargador mas cercano si la bateria es baja y el estado de charging es falso
        if self.energy <= self.low_battery and self.charging == False:
            self.moveToCharger()
            self._register_visit()
            self.energy -= 1
            self.movements += 1
            return
        
        # Condicion de movimiento despues de cargar
        if self.just_finished_charging:
            # Si hay vecino no visitado, priorizarlo
            target = self._pick_unvisited_neighbor()

            if target is not None:
                self.cell = target
                self.energy -= 1
                self.movements += 1
                self._register_visit()
            elif self.return_stack:
                # Si no hay no visitados, usar la ruta de regreso
                coord = self.return_stack.pop()
                x, y = coord
                self.cell = self.model.grid[x, y]
                self.energy -= 1
                self.movements += 1
                self._register_visit()

            # Ya manejamos este "evento"
            self.just_finished_charging = False
            return

        if self.charging == False and self.energy > self.low_battery:
            self.move()
            self._register_visit()
            self.energy -= 1 
            self.movements += 1


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

class ChargingCell(FixedAgent):
    """
    A charging station that appears at a fixed rate and can be used by the roomba to charge its energy.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell=cell