#!/usr/bin/python
#Script to simulate Petri nets

import sys
import argparse
from xml.dom import minidom
#from XMLparse import parse_pnml_input_file
import copy
from copy import deepcopy
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from operator import add
from Progress_bar import Progress_bar

class PetriNetSimulator:
    
    def __init__(self):
        pass
    
    def set_petri_net_model(self, transitions, places, arc_weights_in, arc_weights_out, arc_inhibitors = {}):
        """ MM 24-08-2015 """
        # Set the model
        self.transitions = transitions
        self.places_init = places        
        self.arc_weights_in = arc_weights_in
        self.arc_weights_out = arc_weights_out
        self.arc_inhibitors = arc_inhibitors
        self.place_names = places.keys()
        
        self.places_current = places
        self.num_steps = None
        self.num_sim = None
        
        # Create output matrix for each place
        self.output = { x:[] for x in places.keys() }
        self.transitions_fired = [] # Only saves transitions of last simulation
        self.colors = ['#c0c0c0','#000000','#ff0000','#ffff00','#0000ff','#009000','#ff00ff','#808080','#CC6633']
#        ['#0000FF','#00CC00','#FF00CC','#FFFF00','#000000','#00CCFF','#99CC33','#CCCCCC','#FF6666','#FF99CC','#CC6600','#003300','#CCFFFF','#9900FF','#CC6633','#FFD700','#C0C0C0']
        
    def parse_pnml_input_file(self, pnml):
        transitions = []
        places = {}
        arc_weights_in = {}
        arc_weights_out = {}
        arc_inhibitors = {} #MM 08-09-2015. Inhibitor is always in
        
        doc = minidom.parse(pnml)
        
        #Read in start places
        nodes = doc.getElementsByTagName('place')
        for node in nodes:
            if node.attributes.has_key('id'):
                plac = node.attributes['id'].value
                plac = str(plac)
                #values = 0
                try:
                    values = node.getElementsByTagName('initialMarking')[0].getElementsByTagName('text')[0].firstChild.nodeValue #Maxim 21-08-2015
                    values = float(values)
                except:
                    values = 0
                places[plac] = values
        
        #Read in transitions
        nodes = doc.getElementsByTagName('transition')
        for node in nodes:
            if node.attributes.has_key('id'):
                transition = node.attributes['id'].value
                transition = str(transition)
                transitions.append(transition)
        
        #Read in arcs
        nodes = doc.getElementsByTagName('arc')
        for node in nodes:
            isInhibitorArc = False #MM 08-09-2015
            if node.attributes.has_key('source'):
                sources = node.attributes['source'].value
                sources = str(sources)
                try:
                    values = node.getElementsByTagName('text')[0].firstChild.nodeValue
                    values = float(values)
                except:
                    values = 1

                t = node.getElementsByTagName('type') #08-09-2015
                if t: #08-09-2015
                    isInhibitorArc = t[0].attributes['value'].value == 'inhibitor'
                
                if sources in places:
                    if node.attributes.has_key('target'):
                        targets = node.attributes['target'].value
                        targets = str(targets)
                        if isInhibitorArc: #MM 08-09-2015. InhibitorArc is always a 'in' arc
                            if targets not in arc_inhibitors:
                                arc_inhibitors[targets] = {}
                                arc_inhibitors[targets][sources] = values
                            else:
                                arc_inhibitors[targets][sources] = values
                                
                        else: #Normal arc in
                            if targets not in arc_weights_in:
                                arc_weights_in[targets] = {}
                                arc_weights_in[targets][sources] = values
                            else:
                                arc_weights_in[targets][sources] = values
            
                elif sources in transitions:
                    if node.attributes.has_key('target'):
                        targets = node.attributes['target'].value
                        targets = str(targets)
                        if sources not in arc_weights_out:
                        	arc_weights_out[sources] = {}
                        	arc_weights_out[sources][targets] = values
                        else:
                        	arc_weights_out[sources][targets] = values
        
        self.set_petri_net_model(transitions, places, arc_weights_in, arc_weights_out, arc_inhibitors) #MM 24-08-2015
    
    #SINGLE STEP
    def single_step(self):
        places_temp1 = deepcopy(self.places_current) #Actual place tokens. Consumption and Production
        places_temp2 = deepcopy(self.places_current) #Only consumptions. Used to check whether transition is valid.
        transition_valid = "TRUE"
        transitions_rand = copy.copy(self.transitions)

        transitions_fired_step = [] #MM 28-08-2015, save transitions fired
        while len(transitions_rand) > 0:
            # Draw a random transition and remove from list
            random_int = np.random.randint( 0, len(transitions_rand) ) #Better behaviour than python own random.randint
            t = transitions_rand.pop(random_int)
            
            # Test for enough tokens for this transitions
            for p in self.arc_weights_in[t]:
                if not places_temp2[p] - self.arc_weights_in[t][p] >= 0:
                    transition_valid = "FALSE"
            # Test inhibition. Transition will NOT fire if place contains >= tokens than inhibition weight
            # Note: if inhibited at the start of this step, then stays inhibited all next steps
            if t in self.arc_inhibitors:
                for p in self.arc_inhibitors[t]:
                    if self.places_current[p] >= self.arc_inhibitors[t][p] :
                        transition_valid = "False"

            # If enough tokens, fire the transition
            if transition_valid == "TRUE":
                for p in self.arc_weights_in[t]:
                    if places_temp2[p] - self.arc_weights_in[t][p] >= 1:
                        transition_valid = "TRUE"
                    else:
                        transition_valid = "FALSE"
                    places_temp2[p] = places_temp2[p] - self.arc_weights_in[t][p]
                    places_temp1[p] = places_temp1[p] - self.arc_weights_in[t][p]
                for p in self.arc_weights_out[t]:
                    places_temp1[p] = places_temp1[p] + self.arc_weights_out[t][p]
                transitions_fired_step.append( t ) #save which transition fired
            
            # Add transition to list if still able to fire
            if transition_valid == "TRUE":
                transitions_rand.append(t)
            else:
            	transition_valid = "TRUE"
             
        self.transitions_fired.append( transitions_fired_step )   
        self.places_current = places_temp1 #MM 24-08-2015: update places in the object
            
    #SINGLE SIMULATION
    def single_sim( self, num_steps ):
        #Initialize output for this simulation
        self.token_step_sim = {}
        for place, init_value in self.places_init.iteritems():
            self.token_step_sim[ place ] = [ float(init_value) ]
        
        self.transitions_fired = [] # Only saves transitions of last simulation
        i = 0
        while i < num_steps:
            #Do one step of the simulation
            self.single_step()
            
            #Save step
            for place, place_value in self.places_current.iteritems():
                self.token_step_sim[place].append( float(place_value) )
            i += 1
   
    #MULTIPLE SIMULATIONS
    def multi_sim( self, num_sim, num_steps ):
        self.num_steps = num_steps
        self.num_sim = num_sim
        #Reset the output matrix
        self.output = { x:[] for x in self.place_names }

        i = 0
        progressBar = Progress_bar(cycles_total = num_sim, done_msg = 'time')  #MM 20-08-2015: Progress bar addition, Shows Simulation time afterwards
        while i < num_sim:
            self.places_current = self.places_init #MM 24-08-2015 Reset model
            
            #Do one simulation
            self.single_sim( num_steps )
            
            #Save simulation to output (MM 24-08-2015, moved from single_sim())
            for place, token_steps in self.token_step_sim.iteritems():
                self.output[place].append( token_steps )
                
            progressBar.update() #MM 20-08-2015
            i += 1
            
    def getMeanTokenLevel(self, places, after_step = -1, return_stdev = False ):
        """ Gets the token level after a certain step, averaged over the simulations. 
            Sums tokens if multiple places are given. Also returns st. deviation if specified."""
        if type(places) == str:
            places = [places]
        
        total_token_levels = []
        for sim_i in range( self.num_sim ):
            tokens = [ self.output[place][sim_i][after_step] for place in places ]
            total_token_levels.append( sum(tokens) )
        
        if return_stdev:
            return np.mean( total_token_levels ), np.std(total_token_levels)
        else:
            return np.mean( total_token_levels )
            
    def plotTimeSeries(self, places2plot, doPlotSum = False, label_sum = True,
                       label_suffix = '', colors = None, plotFigure = False,
                       n_trajectories = 1):
        if type(places2plot) == str:
            places2plot = [places2plot]
        
        if not self.output:
            raise Warning("Please perform a simulation first")
        
        if plotFigure is False or plotFigure is True: #Backwards compatibility
            plt.figure() #New figure
        else:
            plt.figure( plotFigure ) #existing figure
            
        if type(colors) == int:
            i = colors #Hack to make cycling to colors possible
        else:        
            i = 0
        if type(colors) != list:
            colors = self.colors # Default set of colors
            
        if doPlotSum:
            totals = []
            for j in range( self.num_sim ):                    
                total = np.zeros( self.num_steps + 1 )
                for place in places2plot:
                    total += np.array( self.output[ place ][j] )
                totals.append(total)
            # Set places2plot to new name. This will plot the sum in the next step
            if label_sum:
                name = label_sum
            else:
                name = '+'.join(places2plot)
            self.output[name] = totals
            places2plot = [name]
        
        for place_name in places2plot:
            if i >= len(colors):
                i = 0
            color = colors[i]
            
            label = "%-12s %s" % (place_name, label_suffix)
            for timeSeries_sim in self.output[place_name][:n_trajectories]:
                plt.plot( timeSeries_sim, color=color, linewidth=3, linestyle='-', label=label )
                i += 1
        plt.ylim(0,None)
        plt.legend(numpoints=1,frameon=True,loc='upper left')
        plt.show()
        
    def plotAverageTimeSeries(self, places2plot, doPlotSum = False, label_sum = '',
                              label_suffix = '', colors = None, plotFigure = False):
        if type(places2plot) == str:
            places2plot = [places2plot]
        
        xdata = range(0, self.num_steps+1, 1)
        
        if plotFigure is False or plotFigure is True: #Backwards compatibility
            plt.figure() #New figure
        else:
            plt.figure( plotFigure ) #existing figure
            
        if type(colors) == int:
            i = colors #Hack to make cycling to colors possible
        else:        
            i = 0
        if type(colors) != list:
            colors = self.colors # Default set of colors
            
        if doPlotSum:
            totals = []
            for j in range( self.num_sim ):                    
                total = np.zeros( self.num_steps + 1 )
                for place in places2plot:
                    total += np.array( self.output[ place ][j] )
                totals.append(total)
            # Set places2plot to new name. This will plot the sum in the next step
            if label_sum:
                name = label_sum
            else:
                name = '+'.join(places2plot)
            self.output[name] = totals
            places2plot = [name]
            
        for place_name in places2plot:
            # Average for every step of every simulation
            averageTimeSeries = np.mean( self.output[place_name], axis=0 )
            stdevTimeSeries = 0.5 * np.std( self.output[place_name], axis=0 )

            color = colors[i]
            label = "%-12s %s" % (place_name, label_suffix)
            plt.plot(xdata, averageTimeSeries, color=color, linewidth=3, linestyle='-', label=label)            
            plt.fill_between(xdata, np.array(averageTimeSeries)-np.array(stdevTimeSeries), np.array(averageTimeSeries)+np.array(stdevTimeSeries), alpha=0.5, edgecolor='#BCB0D4', facecolor='#BCB0D4')
            i += 1
            #Reset colors to start
            if i >= len(colors):
                i = 0
#        plt.ylim(0,None)
        plt.legend(numpoints=1,frameon=True,loc='upper left')
        plt.show()

    def print_transition_sequence(self, places2print = None, outfile = None, step_start = 0, step_stop = None):
        """ Prints a chronological sequence of the transitions fired. Only from the LAST simulation."""
        i = step_start
        if step_stop is None: step_stop = self.num_steps
        if type(outfile) == file:
            out = outfile
        else:
            out = sys.stdout
        
        if not places2print:
            places2print = self.place_names
            
        #output_last_sim = {k:v[-1] for k,v in self.output.iteritems() if k in places2print}
        while i < step_stop:
            print >> out, "Step %d" % i
            # output of last simulation (-1) after step i.
            places = [ "%s:%s" % (place, self.output[place][-1][i]) for place in places2print ]
            #places = {k:"%.1f" % v[i] for k,v in output_last_sim.iteritems()}
            print >> out, "State:", places
            
            for t_fired in self.transitions_fired[i]:
                consumed = [ "%s-%s" % (p,w) for p,w in self.arc_weights_in[ t_fired ].iteritems() ]
                produced = [ "%s+%s" % (p,w) for p,w in self.arc_weights_out[ t_fired ].iteritems() ]
                print >> out, "%3s has fired:" % (t_fired),
                print >> out, "%-37s --> %s" % ( ", ".join(consumed), ", ".join(produced) )
            i += 1
        #Print the last place
        places = [ "%s:%s" % (place, self.output[place][-1][i]) for place in places2print ]
        #places = {k:v[i] for k,v in output_last_sim.iteritems()}
        print >> out, "State:", places
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is a Petri net simulation tool')
    parser.add_argument('-i','--infile', help='pnml input file of the model', required=False)
    args = vars(parser.parse_args())
    
    pnSim = PetriNetSimulator()
    
    if not args['infile']: #default model
        transitions = ["t1","t2","t3","t4","t5","t6","t7","t8","t9","t10","t11"]
        places = {"WNT": 5, "FZD": 5, "LRP": 5, "WNTFZDLRP": 0, "DVL": 5, "WNTFZDLRPDVL": 0, "RC": 0, "Controller": 1, "AXIN": 5, "APC": 5, "CK1": 5, "GSK3": 5, "DC": 0, "DCCTNNB1": 0, "CTNNB1": 0, "ctnnb1": 1, "TCFLEF": 1, "TCFLEFCTNNB1": 0, "axin2":0}
        arc_weights_in = {"t1": {"WNT": 1, "FZD": 1,  "LRP": 1}, 
        "t2": {"WNTFZDLRP": 1, "DVL": 1}, 
        "t3": {"WNTFZDLRPDVL": 1, "AXIN": 1}, 
        "t4": {"RC": 0.1, "Controller": 1}, 
        "t5": {"AXIN": 1, "APC": 1, "CK1": 1, "GSK3": 1}, 
        "t6": {"CTNNB1": 1, "DC": 1}, 
        "t7": {"DCCTNNB1": 1}, 
        "t8": {"DCCTNNB1": 1}, 
        "t9": {"ctnnb1": 1}, 
        "t10": {"CTNNB1": 3, "TCFLEF": 1}, 
        "t11": {"TCFLEFCTNNB1": 1, "axin2":1}}
        arc_weights_out = {"t1": {"WNTFZDLRP": 1}, 
        "t2": {"WNTFZDLRPDVL": 1}, 
        "t3": {"RC": 1}, 
        "t4": {"WNTFZDLRPDVL": 0.1, "AXIN": 0.1, "Controller": 1}, 
        "t5": {"DC": 1}, 
        "t6": {"DCCTNNB1": 1},
        "t7": {"DC": 1}, 
        "t8": {"AXIN": 1, "APC": 1, "CK1": 1, "GSK3": 1},  
        "t9": {"ctnnb1": 1, "CTNNB1":1}, 
        "t10": {"CTNNB1": 2, "TCFLEFCTNNB1": 1}, 
        "t11": {"CTNNB1": 1, "TCFLEF": 1, "AXIN": 1, "axin2": 1}}
        pnSim.set_petri_net_model( transitions, places, arc_weights_in, arc_weights_out ) #MM 24-08-2015
    else:
        pnSim.parse_pnml_input_file( args['infile'] ) #parse model from pnml file

    pnSim.multi_sim(num_sim = 5, num_steps = 100)
    pnSim.plotTimeSeries('CTNNB1',n_trajectories = 10)
