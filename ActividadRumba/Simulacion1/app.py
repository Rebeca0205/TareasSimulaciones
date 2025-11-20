from random_agents.agent import RandomAgent, ObstacleAgent, DirtPatch, ChargingCell
from random_agents.model import RandomModel

from mesa.visualization import (
    Slider,
    SolaraViz,
    make_space_component,
    make_plot_component
)

from mesa.visualization.components import AgentPortrayalStyle

def random_portrayal(agent):
    if agent is None:
        return

    portrayal = AgentPortrayalStyle(
        size=50,
        marker="o",
    )

    if isinstance(agent, RandomAgent):
        portrayal.color = "blue"
    elif isinstance(agent, ObstacleAgent):
        portrayal.color = "gray"
        portrayal.marker = "s"
        portrayal.size = 100
    elif isinstance(agent, DirtPatch):
        portrayal.color = "brown"
        portrayal.marker = "s"
        portrayal.size = 100
    elif isinstance(agent, ChargingCell):
        portrayal.color = "green"
        portrayal.marker = "s"
        portrayal.size = 100

    return portrayal

def post_process(ax):
    ax.set_aspect("equal")

model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "num_agents": Slider("Number of agents", 1, 1, 50),
    "num_obstacle": Slider("Number of obstacles", 50, 1, 100),
    "dirt": Slider("Dirt on the grid", 100, 1, 200),
    "width": Slider("Grid width", 28, 1, 50),
    "height": Slider("Grid height", 28, 1, 50),
}

# Create the model using the initial parameters from the settings
model = RandomModel(
    num_agents=model_params["num_agents"].value,
    num_obstacle=model_params["num_obstacle"].value,
    dirt=model_params["dirt"].value,
    width=model_params["width"].value,
    height=model_params["height"].value,
    seed=model_params["seed"]["value"]
)

space_component = make_space_component(
        random_portrayal,
        draw_grid = False,
        post_process=post_process
)

space_component = make_space_component(
    random_portrayal,
    draw_grid=False,
    post_process=post_process
)

energy_dirty_plot = make_plot_component(["Energy", "Suciedad"])

page = SolaraViz(
    model,
    components=[space_component, energy_dirty_plot],
    model_params=model_params,
    name="Random Model",
)
