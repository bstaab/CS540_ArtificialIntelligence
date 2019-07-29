# cs540_project_green_team
cs540_project_green_team

### Folder Structure

- examples: sample input files (currently from PA2)
- PathPlanner: Kevin's path-planning code adapted from PA2
- vis: visualization module (built on pyglet/OpenGL)

#### To Do

- ~~adapt path planner code with an API to take one/several commands at a time [Kevin]~~ The MovePlanner class now has a planMove method

- select a StanfordNLP wrapper and roll it into this project [Brent]

- write a main program (at the root level) that:
  - lets the user select an initial state
  - loads the visualizer
  - takes a sentence of input

- connect visualizer to path planner state, so it can show what's happening

- feed input through StanfordNLP, and start figuring out how to extract goals out of the resulting parse tree

- at some point, have a mode that takes a whole paragraph of input, splits it into sentences, and feeds each one through the above process


