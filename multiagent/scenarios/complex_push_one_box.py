import numpy as np
from multiagent.core import World, Agent, Landmark
from multiagent.scenario import BaseScenario


class Scenario(BaseScenario):
    """
        One box push domain:
        Two agents push the box and move it to the left target
    """
    def make_world(self):
        world = World()

        # Add agents
        world.agents = [Agent() for i in range(2)]
        for i, agent in enumerate(world.agents):
            agent.name = 'agent %d' % i
            agent.collide = True
            agent.silent = True
            agent.size = 0.1

        # Add boxes
        n_box = 1
        self.boxes = [Landmark() for _ in range(n_box)]
        for i, box in enumerate(self.boxes):
            box.name = 'box %d' % i
            box.collide = True
            box.movable = True
            box.size = 0.25
            box.initial_mass = 7.
            box.index = i
            world.landmarks.append(box)

        # Add targets
        self.targets = [Landmark() for _ in range(n_box)]
        for i, target in enumerate(self.targets):
            target.name = 'target %d' % i
            target.collide = False
            target.movable = False
            target.size = 0.05
            target.index = i
            world.landmarks.append(target)

        # Make initial conditions
        self.reset_world(world)
        
        return world

    def reset_world(self, world):
        # Random properties for agents
        for i, agent in enumerate(world.agents):
            if i == 0:
                agent.color = np.array([1.0, 0.0, 0.0])
            elif i == 1:
                agent.color = np.array([0.0, 1.0, 0.0])
            else:
                raise NotImplementedError()

            agent.state.p_pos = np.random.uniform(-1, +1, world.dim_p)
            agent.state.p_vel = np.zeros(world.dim_p)
            agent.state.c = np.zeros(world.dim_c)

        # Random properties for landmarks
        for i, landmark in enumerate(world.landmarks):
            landmark.color = np.array([0.25, 0.25, 0.25])
            landmark.state.p_vel = np.zeros(world.dim_p)

            if "box" in landmark.name and landmark.index == 0:
                landmark.state.p_pos = np.array([-0.25, 0.0])
            elif "target" in landmark.name and landmark.index == 0:
                landmark.state.p_pos = np.array([-0.85, 0.0])
            else:
                raise ValueError()

    def reward(self, agent, world):
        # NOTE Reward function is negative distance between box0 and target0
        for i, landmark in enumerate(world.landmarks):
            if "box" in landmark.name and landmark.index == 0:
                box0 = landmark
            elif "target" in landmark.name and landmark.index == 0:
                target0 = landmark
            else:
                raise ValueError()

        dist = np.sum(np.square(box0.state.p_pos - target0.state.p_pos))

        return -dist

    def observation(self, agent, world):
        # Get relative positions of all entities
        entity_pos = []
        for entity in world.landmarks:
            entity_pos.append(entity.state.p_pos - agent.state.p_pos)
        assert len(entity_pos) == (len(self.boxes) + len(self.targets))

        # Add other agent relative position
        other_pos = []
        for other in world.agents:
            if other is agent: 
                continue
            other_pos.append(other.state.p_pos - agent.state.p_pos)

        return np.concatenate([agent.state.p_vel] + [agent.state.p_pos] + entity_pos + other_pos)