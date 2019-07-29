# cs540_project_green_team
cs540_project_green_team

### How to Run the Path Planner

        python3 PathPlanner.py <Initial State File> <Goal Requirements File>
	
	
        python3 PathPlanner.py InitialTest.txt InitialGoal.txt

The given example should take ~2 minutes to run, but it's a very robust test.

(Note that the above does not actually work.)

### Description of Path Planner files

- **PathPlanner.py**

	The file that should be executed when running the path planner
	
	Contains all logic for reading and initializing the start state and the goal 
	
	Contains the relationship planner

- **MovePlanner.py**

	Contains the logic for planning a specific move, for example:
		block1 to (1,2,3)

- **State.py**

	Contains all the logic for creating and modifying the current state of the Blocks World

- **Requirements.py**

	Contains all the requirements that the state must meet before the algorithm reaches completetion
	
	Also handles all the logic related to wildcard bindings

- **Block.py**

	Contains all the attributes related to an individual block and methods to set and modify them



### Updates

- The MovePlanner class now has a planMove method which takes a single move (A tuple of strings of the form (block1_id, move, block2_id) where move is one of: "above", "next-to", "slide-next-to", "slide-to", or "move-to") and the current state of the blocks world, and returns the moves it found and the number of unique states it visited. An example execution of this command can be found in Main.py


#### Notes

I won't object if you guys want to modify the code (just make sure the modifications work before pushing them)

I'm aware that I essentially implemented the same A* algorithm twice, and there are a number of methods which take paramters that don't appear to be used

Finally, if there are any questions, let me know!
