# PAD_AlgorithmicSolver

PAD-AS
 A game solver to automate Puzzle&Dragons game on an emulator on a computer

 Languages: [English](README.md), [日本語/Japanese](README.jp.md)
 - [General and Getting Started](#getting-started)
     - [Introduction](#intro)
     - [Dependencies](#dependencies)
     - [Installation](#instalation)
 - [How Does PAD_AlgorithmicSolver Work?](#how-does-it-work)
     - [General overview of the Algorithm](#general-overview)
     - [Techiques](#techniques)
     - [Performance](#performance)
 - [Explanatory Notes](#explanation)
     - [Options in the GUI](#option-gui)
     - [Limitation](#limitation)



--- 
<a id = "getting-started"></a> 
## General and Getting Started

---
<a id = "intro"></a> 
### Introduction
This project was started because I play the JP version of PAD and I wanted to play using 2 player mode.  I got an emulator (NOX) on my pc but playing PAD on my PC was hard, so I thought "hey, I should make a solver that plays the game for me, then I can play multiplayer with my pc and smartphone"

---
<a id = "dependencies"></a> 
### Dependencies

---
<a id = "instalation"></a> 
### Installation


---
<a id = "how-does-it-work"></a> 
## How Does PAD_AlgorithmicSolver Work?
 - 1.) Take screenshot, checks if a board exist
    - Visualizing it is optional
 - 2.) Make and store an array of the board
 - 3.) Create partitions and find a "good" permutaion
 - 4.) retrieve Info from GUI
 - 5.) Filter for partitions that meet user's requiement
 - 6.) Create/start simulation
 - 7.) Find shortest path for each orbs, end position pairs
 - 8.) Move and update board state
 - 9.) See if some of the moves can be shorted
 - 10.) Move the mouse based on the outcome of the simulation
 - 11.) Repeat


---
<a id = "general-overview"></a> 
### General overview of the Algorithm


---
<a id = "techniques"></a> 
### Techniques



---
<a id = "performance"></a> 
### Performance


---
<a id = "explanation"></a> 
## Explanatory Notes


---
<a id = "option-gui"></a>
### Options in the GUI



---
<a id = "limitation"></a>
### Known Limitations
- Obviously new gimics are limitations
- I still haven't modified the priority to have bomb drops included
- 7x6, 5x4 is still in test phase
