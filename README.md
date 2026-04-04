# 🐜 Pixel Art — Ant Colony Simulation (Mesa + Hex Grid)

A phase-driven **ant colony simulation built in Python using Mesa**, focused on **emergent colony behavior, caste dynamics, and lifecycle progression**.

This project models the **three ant castes**:

* 👑 Queen
* 🐜 Worker
* 🪽 Drone

Across the **three colony stages**:

* **Founding**
* **Growth**
* **Reproductive**

The simulation currently includes a **Phase 0 foundation architecture**, using a **hexagonal world grid** with **dynamic cell density layers** to support future expansion into pheromones, tunneling, foraging, and colony competition.

---

# ✨ Vision

The goal of this project is to simulate how **simple agent rules create complex colony intelligence**.

The long-term roadmap includes:

* emergent worker specialization
* pheromone pathfinding
* brood lifecycle
* resource economies
* reproductive flights
* daughter colony spawning
* multi-colony territorial conflict
* swarm optimization experiments

This project is also designed as a **research + portfolio simulation system** that can later evolve into:

* Ant Colony Optimization (ACO)
* swarm robotics prototypes
* city logistics simulations
* distributed workforce coordination systems

---

# 🧱 Current Architecture

```text
Project Structure for: pixel_art
├── core
│   ├── agents
│   │   ├── __init__.py
│   │   ├── base_ant.py
│   │   ├── drone.py
│   │   ├── queen.py
│   │   └── worker.py
│   ├── world
│   │   ├── __init__.py
│   │   └── cell.py
│   ├── __init__.py
│   └── model.py
├── rendering
│   ├── __init__.py
│   └── renderer.py
├── utils
│   └── tree.py
├── .gitignore
└── main.py
```

---

# 🧠 Core Design Principles

## 1) Hexagonal World

The colony runs on a **hex grid** rather than a square grid.

This improves:

* natural movement directions
* more realistic spatial diffusion
* smoother pheromone spread
* better tunnel expansion geometry
* superior neighborhood calculations

This makes the simulation ideal for:

* exploration
* territory growth
* local interaction rules
* path emergence

---

## 2) Dynamic Density Cells

The world supports **low-density and high-density cells**.

This allows terrain and nest structures to evolve into:

* sparse outer terrain
* dense nest chambers
* traffic-heavy tunnel routes
* food-rich zones
* blocked / dangerous regions

Future use cases:

* congestion simulations
* preferred trail systems
* tunnel collapse risk
* local traffic heatmaps

---

## 3) Caste-Based Agents

Each caste is isolated into its own implementation layer.

## 👑 Queen

Responsible for:

* colony survival
* brood production
* stage transitions
* reproductive switching

## 🐜 Worker

Responsible for:

* food gathering
* brood care
* defense
* tunnel expansion
* pheromone maintenance

## 🪽 Drone

Reserved for:

* reproductive stage
* mating flight behavior
* colony expansion genetics

---

# 🚀 Development Roadmap

## ✅ Phase 0 — Foundation (Current)

Implemented:

* project structure
* hex world
* cell abstraction
* caste separation
* renderer foundation
* simulation entry point

This phase establishes the **software architecture required for emergence**.

---

## 👑 Phase 1 — Founding

Planned features:

* queen energy system
* first egg laying
* brood incubation
* first worker spawn
* early nest survival

Goal:

> a single queen successfully bootstraps a colony.

---

## 🐜 Phase 2 — Growth

Planned features:

* worker role switching
* foraging logic
* food economy
* pheromone trails
* nest expansion
* tunnel density shaping

Goal:

> transform the colony into a distributed intelligent system.

---

## 🪽 Phase 3 — Reproductive

Planned features:

* drone production
* reproductive queens
* mating zones
* colony splitting
* daughter nests

Goal:

> allow self-replication and ecosystem simulation.

---

# 🛠️ Tech Stack

* **Python**
* **Mesa**
* **Hex-grid simulation model**
* custom renderer pipeline
* modular agent architecture

---

# ▶️ Running the Project

```bash
python main.py
```

As the project evolves, optional launch modes may include:

```bash
python main.py --phase founding
python main.py --render ascii
python main.py --render pixel
```

---

# 📊 Future Metrics

The simulation is being designed to support deep metrics collection.

Examples:

* colony population
* caste ratios
* food efficiency
* tunnel traffic density
* pheromone strength
* worker lifespan
* queen fertility
* colony expansion radius

These metrics will make the simulator useful for:

* experimentation
* AI swarm research
* optimization studies
* educational visualization

---

# 🌱 Why This Project Matters

This project explores a fascinating question:

> How does intelligence emerge from simple local rules?

Ant colonies are one of the best real-world examples of:

* decentralized coordination
* adaptive task switching
* resilient logistics
* collective memory
* scalable self-organization

This repo is the beginning of that exploration.

---

# 📌 Next Milestone

The next major milestone is:

> **Phase 1 — Queen founding lifecycle**

Recommended implementation order:

1. queen energy decay
2. egg queue
3. incubation timer
4. worker hatch
5. phase transition to growth

---

# 🤝 Contribution Philosophy

The codebase is intentionally modular so that future work can plug into:

* new caste types
* new terrain systems
* pheromone engines
* optimization strategies
* machine learning decision layers

The architecture is built for experimentation.

---

# ⭐ Long-Term Goal

Turn this into a **beautiful emergent simulation sandbox** where colony behavior becomes a lens for:

* biology
* distributed systems
* AI
* optimization
* social coordination

A small colony.
Simple rules.
Unexpected intelligence.
