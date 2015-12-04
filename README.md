# Petri-net-simulation

***

For a simple example of how to use the Petri net simulation script, see `example_usage.py`.

## Plotting functions

- `.plotTimeSeries( places2plot [,doPlotSum, label_sum, label_suffix, colors, plotFigure, n_trajectories] )`
  - `places2plot` -- a list of strings containing the names of the places to be plotted
  - `doPlotSum` -- if `True`, only the sums of the tokens of the places specified in `places2plot` are plotted. (default `False`)
  - `label_sum` -- a string with a custom label for the sum. (default `None`)
  - `label_suffix` -- a string, appended to the place name in the legend of the plot. (default `''`)
  - `colors` -- a list of color names to be used. If not enough colors specified, this list is reused. (default `None` = default list of colors)
  - `plotFigure` -- integer specifying in which plotnumber to plot. Used for plotting multiple times in the same window. (default `None` = new window)
  - `n_trajectories` -- integer specifying how many trajectories are plotted, if multiple simulations have been simulated.  (default `1`)
- `.plotAverageTimeSeries( places2plot [,doPlotSum, label_sum, label_suffix, colors, plotFigure] )`
  - *Same as `.plotTimeSeries()`, excluding the `n_trajectories` parameter*


## Analysis functions
- `.print_transition_sequence( [places2print, outfile, step_start, step_stop] )`
- `.getMeanTokenLevel( place [,after_step, return_stdev] )`
