import boolean2pew as b2p
import cubewalkers as cw

class ensemble_simulation:

    def __init__(self, rules ,initial_state='default_all_off',update_mode='async',steps=100,ensemble_size=10,shuffler='default',node_order='default',global_error_prob = 0):

        self.rules=rules
        self.steps=steps
        self.ensemble_size=ensemble_size
        self.shuffler=shuffler
        self.update_mode=update_mode
        self.global_error_prob = global_error_prob
        
        self.model = b2p.Model(rules, mode=update_mode)
        if initial_state=='default_all_off':
            self.initial_state=dict(zip(model.nodes,[0 for i in range(len(model.nodes))]))
        else:
            assert initial_state.keys()==self.model.nodes, 'Invalid node keys in initial_state!'
            self.initial_state=initial_state

        if node_order=='default':
            self.node_order=list(self.model.nodes)
        else:
            assert set(node_order)==self.model.nodes, 'Invalid node list in node_order'
            self.node_order=node_order


        self.simulation_ran=0

    def simulate_manipulated_ensemble(self, manipulation_set, simulation_method):
    
        if simulation_method == 'cubewalkers': 
            return self.simulate_manipulated_ensemble_cubewalkers(manipulation_set)
        elif simulation_method == 'booleannet':
            return self.simulate_manipulated_ensemble_booleannet(manipulation_set)
        else:
            raise ValueError('Not a valid simulation method')

    def simulate_manipulated_ensemble_booleannet(self, manipulation_set):

        import numpy as np
        self.manipulation_set=manipulation_set
        from tqdm import tqdm
        self.stop_time_list=[]
        self.average_state_list=[]
        self.final_states=[]

        self.states_array_ensemble=np.zeros((self.steps+1,len(self.node_order),self.ensemble_size))
        #self.model = b2p.Model(rules, mode=update_mode)
        for ens in tqdm(range(self.ensemble_size)):
            self.model.initialize(lambda node: self.initial_state[node])

            self.color_mask=np.zeros((self.steps+1, len(self.node_order)))

            
            for t in range(self.steps):
                for ms in self.manipulation_set:
                    if t>=ms['start_time'] and t<ms['end_time']:
                        if np.random.binomial(1,ms['success_probability']):
                            self.model.states[-1][ms['node']]=ms['enforced_state']
                            self.color_mask[t,self.node_order.index(ms['node'])]=int(ms['enforced_state'])+2

                if self.shuffler!='default':
                    self.model.iterate(1, shuffler=self.shuffler)
                else:
                    self.model.iterate(1)


            states_array=np.array([[state[i] for i in self.node_order] for state in self.model.states])
            
            self.states_array_ensemble[:,:,ens]=states_array

            self.simulation_ran=1
            
        #here the array is defined by the node order list in the states_array = ... line    
        self.array_node_order_dict = {v:k for k,v in enumerate(self.node_order)} 
        
        return 1

    def simulate_manipulated_ensemble_cubewalkers(self, manipulation_set):

        import numpy as np
        self.manipulation_set=manipulation_set
        
        cw_compatible_initial_state='\n'.join(node_name+', '+str(state) for node_name,state in self.initial_state.items())
        
        cw_compatible_experiment = ''
        for experiment in manipulation_set:
            cw_compatible_experiment+=','.join([experiment['node'],
                                                str(experiment['start_time']),
                                                str(experiment['end_time']),
                                                str(experiment['enforced_state'])])+'\n'

        cw_compatible_rules = self.naive_pew_to_pbn_conversion(self.rules)

        #print(cw_compatible_rules)

        if self.global_error_prob>0:
            
            noisy_rules = ""
            for line in cw_compatible_rules.splitlines():
                if not line.strip():
                    continue
                f, r = line.split("* =")
                if f.strip() == r.strip(): #I dont want the inputs to be noisy
                    noisy_rules += f"{f}*=\t({r.strip()})\n"
                    continue
                noisy_rules += f"{f}*=\t({r.strip()}) != (0<<={self.global_error_prob})\n"
            cw_compatible_rules = noisy_rules

        #print(cw_compatible_rules)

        cw_experiment=cw.Experiment(cw_compatible_experiment)
        
        cw_model = cw.Model(cw_compatible_rules,
                             experiment=cw_experiment,
                             n_walkers=self.ensemble_size, 
                             n_time_steps=self.steps,
                             initial_biases=cw_compatible_initial_state)
        self.cw_model = cw_model       
        if self.update_mode == 'async':
            cw_model.simulate_ensemble(maskfunction=cw.update_schemes.asynchronous_PBN, averages_only=False)
            self.simulation_ran=1
        elif self.update_mode == 'sync': 
            cw_model.simulate_ensemble(maskfunction=cw.update_schemes.synchronous_PBN, averages_only=False)
            self.simulation_ran=1
        else:
            print(self.update_mode, ' is not a valid update scheme. Try "sync" or "async".')
            
        self.states_array_ensemble = cw_model.trajectories.get()
        self.array_node_order_dict = cw_model.vardict
        return 1        
    

    def plot_average_trajectories(self,nodes='all', figsize=(10,6), fontsize=16, grid=True, linewidth=1, title='', line_props={}, ax=None):

        from matplotlib import pyplot as plt
        import numpy as np
        import seaborn as sns
        assert self.simulation_ran==1, 'No simulation data to plot yet. See method "simulate_ensemble..."'
        if nodes=='all':
            nodes=self.node_order
        average_trajectories=np.mean(self.states_array_ensemble,axis=2)
        if ax == None:
            f, ax = plt.subplots(figsize=figsize)
        plt.rcParams['font.size'] = str(fontsize)
        for node in nodes:
            n=self.array_node_order_dict[node]
            
            if node in line_props:
                ax.plot(range(self.steps+1),average_trajectories[:,n], **line_props[node])
            else:
                ax.plot(range(self.steps+1),average_trajectories[:,n], linewidth=linewidth, label=node)
            #plt.errorbar(range(len(avg_evolution)),avg_evolution[:,n], yerr=np.sqrt(std_evolution[:,n]), label=node_order[n])
        ax.set_xlabel('Steps')
        ax.set_ylabel('Average node value')
        ax.legend(bbox_to_anchor=(1.04,1), loc="upper left")
        if title!='':
            ax.set_title(title)
        if grid==True:
            ax.grid()
        sns.despine()
        return ax

    def average_state_of_time_slice(self,start_time,end_time):
        import pandas as pd
        return pd.DataFrame(self.states_array_ensemble[:,start_time:end_time,:].mean(axis=1),columns=self.node_order)

    def average_state_of_ensemble_in_time_slice(self,start_time,end_time):
        import pandas as pd
        return pd.DataFrame(self.states_array_ensemble[:,start_time:end_time,:].mean(axis=0),columns=self.node_order)
        
    def savitzky_golay(self, y, window_size, order, deriv=0, rate=1):
        r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
        The Savitzky-Golay filter removes high frequency noise from data.
        It has the advantage of preserving the original shape and
        features of the signal better than other types of filtering
        approaches, such as moving averages techniques.
        Parameters
        ----------
        y : array_like, shape (N,)
            the values of the time history of the signal.
        window_size : int
            the length of the window. Must be an odd integer number.
        order : int
            the order of the polynomial used in the filtering.
            Must be less then `window_size` - 1.
        deriv: int
            the order of the derivative to compute (default = 0 means only smoothing)
        Returns
        -------
        ys : ndarray, shape (N)
            the smoothed signal (or it's n-th derivative).
        Notes
        -----
        The Savitzky-Golay is a type of low-pass filter, particularly
        suited for smoothing noisy data. The main idea behind this
        approach is to make for each point a least-square fit with a
        polynomial of high order over a odd-sized window centered at
        the point.
        Examples
        --------
        t = np.linspace(-4, 4, 500)
        y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
        ysg = savitzky_golay(y, window_size=31, order=4)
        import matplotlib.pyplot as plt
        plt.plot(t, y, label='Noisy signal')
        plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
        plt.plot(t, ysg, 'r', label='Filtered signal')
        plt.legend()
        plt.show()
        References
        ----------
        .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
           Data by Simplified Least Squares Procedures. Analytical
           Chemistry, 1964, 36 (8), pp 1627-1639.
        .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
           W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
           Cambridge University Press ISBN-13: 9780521880688
        """
        import numpy as np
        from math import factorial
        
        try:
            window_size = np.abs(np.int(window_size))
            order = np.abs(np.int(order))
        except ValueError:
            raise ValueError("window_size and order have to be of type int")
        if window_size % 2 != 1 or window_size < 1:
            raise TypeError("window_size size must be a positive odd number")
        if window_size < order + 2:
            raise TypeError("window_size is too small for the polynomials order")
        order_range = range(order+1)
        half_window = (window_size -1) // 2
        # precompute coefficients
        b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
        m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
        # pad the signal at the extremes with
        # values taken from the signal itself
        firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
        lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
        y = np.concatenate((firstvals, y, lastvals))
        
        return np.convolve( m[::-1], y, mode='valid')

    def naive_pew_to_pbn_conversion(self, rules):
        '''
        naive (non-recursive, non-nested) conversion of the pew syntax into cubewalker compatible PBN syntax
        e.g. 
        
        A*=[0.1,0.8] C  --> A * = (((0<<=0.1) & C) | ((0<<=0.8) & not C))
        
        it can also deal with one layer of parantheses:
        
        A*=[0.1,0.8] (B and C) --> A * = (((0<<=0.1) & ( B and C )) | ((0<<=0.8) & not ( B and C )))
        
        WARNING! Nested parantheses and multiple PEW operators in the same row will not work with this version!
        '''
        
        
        model = b2p.Model(rules, mode=self.update_mode)
        cw_compatible_rules = ''
        #extract pew operators and the clauses/nodes from the boolean rules
        for rule in model.tokens:
            i=0
            reconstructed_rule = []
            while i < len(rule):
                token = rule[i]
                j=1
                #print(i, 'token',token)
                if token.type=='PEW':
                   # print('pew_token',token.value)
                    pew_token = token.value
                    p1,p2=eval(pew_token)
                    if rule[i+1].type == 'ID':
                        target_clause=rule[i+1].value
                        #print('target clause:', rule[i+1].value)
                        j+=1
                    elif rule[i+1].type == 'LPAREN':
                        right_paren_found=False
                        clause=[]

                        while not right_paren_found:
                            clause.append(rule[i+j].value)
                            if rule[i+j].type == 'RPAREN':
                                right_paren_found=True
                            j+=1
                        target_clause =  ' '.join(clause)
                        #print('target clause:',target_clause)
                    PBN_syntax = '(((0<<=%s) & %s) | ((0<<=%s) & not %s))'%(str(p1),target_clause,str(p2),target_clause)
                    reconstructed_rule.append(PBN_syntax)
                else:
                    reconstructed_rule.append(token.value)
                i+=j
            #print(reconstructed_rule)
            cw_compatible_rules+=' '.join(reconstructed_rule)+'\n'
        return cw_compatible_rules

