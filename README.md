# Petri-net-simulation

Class for simulating [Petri net](https://en.wikipedia.org/wiki/Petri_net) models using maximal parallelism execution ("execute greedily as many transitions as possible in one step" [[1]](http://www.cs.vu.nl/~wanf/pubs/fmsb08.pdf)). The class includes plotting and analysis methods for quick visualisation of the simulation result. The Petri net model has to be supplied as a pnml file.

This script was developed during an internship project at the VU University Amsterdam.

***

For a simple example, see `example.py`. This example uses a extensive Petri net model of the Wnt/beta-catenin pathway (`wnt_model.pnml`).

## Initiate object and load model
```
pnSim = PetriNetSimulator()
pnSim.parse_pnml_input_file( '<your_model.pnml>' )
```

## Simulate
`pnSim.multi_sim(num_sim, num_steps)`


## Plotting functions

- `pnSim.plotTimeSeries( places2plot [,doPlotSum, label_sum, label_suffix, colors, plotFigure, n_trajectories] )`
  Plots the time series of one or multiple simulations at each step.
  - `places2plot` -- a list of strings containing the names of the places to be plotted.
  - `doPlotSum` -- if `True`, only the sums of the tokens of the places specified in `places2plot` are plotted. (default `False`)
  - `label_sum` -- a string with a custom label for the sum. (default `None`)
  - `label_suffix` -- a string, appended to the place name in the legend of the plot. (default `''`)
  - `colors` -- a list of color names to be used. If not enough colors specified, this list is reused. (default `None` = default list of colors)
  - `plotFigure` -- integer specifying in which plotnumber to plot. Used for plotting multiple times in the same window. (default `None` = new window)
  - `n_trajectories` -- integer specifying how many trajectories are plotted, if multiple simulations have been simulated.  (default `1`)
- `pnSim.plotAverageTimeSeries( places2plot [,doPlotSum, label_sum, label_suffix, colors, plotFigure] )`
  Plots the average number of tokens at each step.
  - *Parameters are the same as `.plotTimeSeries()`, excluding the `n_trajectories` parameter*


## Analysis functions
- `pnSim.print_transition_sequence( [places2print, outfile, step_start, step_stop] )`
  Prints for each step the transitions fired in that step and the resulting number of tokens (available for the next step).
  - `places2print` -- the number of tokens of these places are printed. (default all places)
  - `outfile` -- the file where the transition sequence is written to. (default sys.stdout)
  - `step_start` -- start printing from this step onwards.
  - `step_stop` -- print unil this number of steps.
- `pnSim.getMeanTokenLevel( place [,after_step, return_stdev] )`
  - `place` -- Name of the place for which the mean token level is retrieved.
  - `after_step` -- integer. The mean token level after this step is returned. (default last step)
  - `return_stdev` -- if `True`, returns a set of two values; the mean and the standard deviation. (default `False`)
