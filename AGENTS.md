# Agent Architecture & Physiology

This document outlines the implementation details of the ants and environmental agents in the `pixel_art` colony simulation, specifically focusing on the transition to **Mesa 3.0+** standards.

## 🛠 Tech Stack: Mesa 3.0+ Standards
In this project, we have moved away from the legacy Mesa `Scheduler` pattern to the modern **AgentSet** pattern introduced in Mesa 3.0.

- **No `self.schedule`**: The model no longer uses a separate scheduler object. All agents are automatically tracked in `self.agents` upon initialization.
- **`self.agents.shuffle_do("step")`**: Used in `model.step()` to advance all agents in a random order.
- **`self.remove()`**: Agents are removed from both the Grid and the Model simultaneously using the built-in `self.remove()` method.
- **`self.steps`**: Model-level step counting is handled via `self.steps` instead of `self.schedule.steps`.

---

## 🐜 Ant Physiology (BaseAnt)
All ant castes inherit from `BaseAnt`, which manages the core biological simulation:

- **Energy**: Constant drain via `metabolism_rate`. Restored by `eat()`.
- **Health**: Decreases if `energy <= 0` (Delayed Starvation).
- **Recovery**: Ants slowly regain health if energy is > 50%, at a higher metabolic cost.
- **Age**: Ants have a `max_age` after which they die naturally.

---

## 🐣 Brood Life Cycle (BroodAgent)
The colony growth is managed through a multi-stage developmental pipeline:

1.  **EGG**: Laid by the Queen. Develops automatically over time.
2.  **LARVA**: Requires active **Feeding** by Workers. If not fed, they will never pupate.
3.  **PUPA**: Development is automatic once the larval food requirement is met.
4.  **ADULT**: Hatches into a `WorkerAgent` (or occasionally a `DroneAgent` during Reproductive phase).

---

## 📋 Ant Castes & Behaviors

### QueenAgent
- **Role**: Reproduction and Phase Control.
- **Logic**: Egg-laying rate scales with colony phase (`ERGONOMIC` phase doubles production).
- **Self-Preservation**: Consumes colony food stockpile to maintain high energy.

### WorkerAgent
- **Task Switching**: Dynamically switches between `FORAGING` and `NURSING` based on:
    - **Colony Phase**: Focuses on growth in `ERGONOMIC` and surplus in `REPRODUCTIVE`.
    - **Resource Levels**: Prioritizes foraging if food is low.
    - **Brood Needs**: Prioritizes nursing if larvae are present.
- **Navigation**: Uses a combination of "Scent" (attraction zones around food) and "Pheromones" (trail following).

### DroneAgent
- **Role**: Reproduction.
- **Logic**: High metabolism, consumes colony food.
- **Mating**: Only active during the `REPRODUCTIVE` phase; removes itself upon successful mating.

---

## 🌍 Environmental Agents

### PheromoneCell / NestCell
- Manages pheromone intensity and decay.
- `NestCell` marks the home base where food is stockpiled and brood is kept.

### FoodSource
- Contains a finite amount of resource.
- Can be harvested by Workers and has a very slow natural regrowth rate.
