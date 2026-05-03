from femtobot import create_agent
from pathlib import Path


if __name__ == '__main__':
    path = Path(__file__).parents[1] / 'imgs/graph.png'
    agent, _ = create_agent()
    with path.open('wb') as f:
        f.write(agent.get_graph(xray=True).draw_mermaid_png())
