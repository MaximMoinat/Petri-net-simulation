#!/usr/bin/python
"""
Example of Petri Net Simulator usage
"""

from PetriNetSimulator import PetriNetSimulator

# Initiate object
pnSim = PetriNetSimulator()

# Load the model from .pnml
pnSim.parse_pnml_input_file( 'example_model.pnml' )

# Execute 10 simulations of 100 steps (maximal parallel execution)
pnSim.multi_sim(num_sim = 10, num_steps = 100)

# Plot the time serie of each simulation trajectory of the CTNNB1 place
pnSim.plotTimeSeries( 'CTNNB1', n_trajectories = 10 )
# Plot the average with shaded standard deviation
pnSim.plotAverageTimeSeries( 'CTNNB1' )
