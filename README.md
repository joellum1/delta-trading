# 🏦 IMC Trading - Prosperity 3 Competition 🧠📈

Welcome to **Team Delta's** repository for the **IMC Trading's Prosperity 3** competition. This repo contains our team's solution, trading strategies, and research conducted during the competition.

## 📌 Overview

The **Prosperity 3** competition challenges participants to develop an algorithmic trading agent capable of operating in a simulated exchange environment. The goal is to maximize profit while maintaining resilience and adaptability to market conditions.

---

## 📄 Prosperity 3 Wiki

[Prosperity 3 Wiki Page Link](https://imc-prosperity.notion.site/Prosperity-3-Wiki-19ee8453a09380529731c4e6fb697ea4) 

---

## 📦 Getting Started

This project uses a virtual environment to manage dependencies. Only the following libraries are supported and installed:

- [`pandas`](https://pandas.pydata.org/)
- [`numpy`](https://numpy.org/)
- [`jsonpickle`](https://pypi.org/project/jsonpickle/)
- Built-in Python libraries: `math`, `statistics`, `typing`

Run the following script to set up your virual environment.

```bash
python setup_env.py
```

Make sure to **activate the environment before running your bot** so that it uses only the allowed dependencies.

### On **Mac/Linux**:

```bash
source venv/bin/activate
```

### On **Windows**:

```bash
venv\Scripts\activate
```

After activation, your terminal should show a prefix like:

```bash
(venv) $
```

To **deactivate**, simply run:

```bash
deactivate
```

---

## 🛠️ Project Details

After running the simulation and receiving the logs, use the [visualisation tool](https://jmerle.github.io/imc-prosperity-3-visualizer/) (source code found in https://github.com/jmerle/imc-prosperity-3-visualizer) to generate graphical report of the algorithm's performance.

### Round 1

In Round 1, we were introduced to three commodities available for trading:

- 🌿 **Rainforest Resin** — A relatively **stable** commodity.
- 🦑 **Squid Ink** — Known to be **unpredictable** and **volatile**.
- 🪸 **Kelp** — Also **volatile**, with less consistent market behavior.

The varying stability of these assets introduced an interesting challenge. Rainforest resin offered predictable behavior, while squid ink and kelp required more caution and adaptability.

With no prior experience in algorithmic trading, we focused on simplicity over sophistication. We chose to calculate the acceptable price for placing buy and sell orders as the **mid-price of the previous bid-ask spread**. This gave us a neutral baseline to start trading without overcommitting to unverified assumptions or complex predictions.

### Round 2

In Round 2, the set of tradable goods changed significantly, introducing a mix of individual items and bundled products:

- 🥐 **Croissant**  
- 🍓 **Jam**  
- 🪘 **Djembe**  
- 🧺 **Picnic Basket 1** — Contains **6 croissants**, **3 jams**, and **1 djembe**  
- 🧺 **Picnic Basket 2** — Contains **4 croissants** and **2 jams**

This round introduced the concept of **composite goods**, where the value of the baskets was inherently tied to the value of their individual components. It challenged us to think beyond isolated asset pricing and explore relationships between bundled and base commodities.

We are currently exploring **strategic arbitrage between the baskets and their components** as a key opportunity — though this also adds a layer of complexity in managing **value equivalency**, **price fluctuations**, and **potential trade-offs**.

