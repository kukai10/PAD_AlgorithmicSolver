# PAD_AlgorithmicSolver

PAD-AS
 A game solver to automate Puzzle&Dragons game on an emulator on a computer


## Updates and important info: 
- The android emulator, NOX, doesnt support the new update of PAD, so wait few weeks for the new PAD to be compatible.

---

 Languages: [English](README.md), [日本語/Japanese](README.jp.md)
 - [General and Getting Started](#getting-started)
     - [Motivation for the Project](#intro)
     - [Dependencies](#dependencies)
     - [Installation](#instalation)
 - [How Does PAD_AlgorithmicSolver Work?](#how-does-it-work)
     - [General overview of the Algorithm](#general-overview)
     - [Techniques](#techniques)
     - [Performance](#performance)
 - [Explanatory Notes](#explanation)
     - [Options in the GUI](#option-gui)
     - [Limitation](#limitation)



--- 
<a id = "getting-started"></a> 
## General and Getting Started
This program is an automated puzzle solver that works on any computer.  The solver will take screenshots and search for a PAD screen and it will play the game using the 


this program will take into account the following when it is solving the board:
 - leader skills(any # of color connected, erase # of color orbs, combo skills, 5+ connected, 7x6, no drop)
 - awoken skills(7c, 10c, 2way, heart piercier, void damage piercer, type killers, 80% < HP buff, 50% > HP buff)
 - player buffs(atk up, def up, status buff from leader skill)
 - enemy buffs(def up, combo absorbtion, element absorption, damage absorbtion, void damage, guts)
 - board gimics(poison, jammer, darkness, tapes, cloud)
 
The feature that I am fond of:
 - human like movements(hesitation, small bits of randomness)
 - If the option is turned on, it will make descisions like doing 1 combo to gain skill turn
 - solver that takes into account most gimics
 - adaptability of the solver
instructions from the user-interface.

pic of gui 

gif of solver


---
<a id = "intro"></a> 
### Motivation for the Project
This project was started because many people, myself included, are not able to utilize 2-player mode; reasons for this is because they don't have a second phone, or no friends who plays the JP version, or because its late at night and everyone is asleep, etc.
I knew that there are emulators on that can run PAD, I use [NOX](), however unless your computer is touchscreen, there's no easy way of manipulating the board.  After learning some python, I made this my first personal project and I believe there are many people who are in the same shoes as me, so I made this public.
I don't care if I get cited when this project is used online, please give credit to [guy who made the cv2 lib](#) because although my modified version is powerful that his, the base of that part of the code is from him.


---
<a id = "dependencies"></a> 
### Dependencies
 - CV2
 - pygame
 - numpy
 - PyAutoGui
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






For a given board, we find few candidates that could be the final state of the board.  Then for each potential final state we add weights, the weights are going to be the distance from the initial to the final position, if the orb is in the right position, we assign -5 as it's weight.  If the algorithm finishes a task (i.e. connect some # of orbs) it gets rewarded by -10.
The reason I have weights is do somesthing similar to a greedy-algorithm, at each point the algorithm will decide which vertical or horizontal move will minimize the total weights.


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
