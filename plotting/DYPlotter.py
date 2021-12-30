import pandas as pd
import numpy as np
import scipy.stats
import yaml
import pickle



class DYPlotter(object):
    """
    Class with useful functions for making DYData/DYMC validation plots

    :param root_obj: object containing dfs needed for plotting, with no preselection applied
    :type : ROOTHelpers
    :param cut_map: dictionary of form {variable_name:cut_applied}
    :type : dict
    :param mc_total: binned mc for the variable being plot. Note that the weights used in this sum are reweighted by pT
    :type : numpy 1D array
    :param mc_totals_no_pt_rew: binned mc for the variable being plot for a given bkg process Note that the weights used in this sum are NOT reweighted by pT
    :type : numpy 1D array
    :param mc_stat_uncs: statistical uncertainties for each bin. First entry is array of lower bounds,
     second is array of upper bounds
    :type : list
    :param k_factor: normalisation between data and MC for given variable
    :type : float
    :param clf: classifier being evaluated
    :type : XGBClassifier() (or similar)
    :param proc: name of the process that the classifier targets e.g. VBF (BDT/NN)
    :type: str
    """

    def __init__(self, root_obj, cut_map): 
        self.root_obj             = root_obj    
        self.cut_map              = cut_map

        self.mc_total             = None
        self.mc_totals_no_pt_rew  = {}
	self.mc_stat_uncs         = None
	self.k_factor             = None
        self.clf                  = None
        self.proc                 = None
        self.colours              = ['lightgrey','#CBCBE5'] #VBF
        #self.colours              = ['#CBCBE5'] #ggH

    def read_and_concat_dfs(self, reload_samples):
        """ read in dfs """

        for bkg_obj in self.root_obj.bkg_objects:
            self.root_obj.load_mc(bkg_obj, bkg=True, reload_samples=reload_samples)
        for data_obj in self.root_obj.data_objects:
            self.root_obj.load_data(data_obj, reload_samples=reload_samples)
        self.root_obj.concat()

        print 'bkg mc variables'
        print self.root_obj.mc_df_bkg.columns[:]
        print 'data variables'
        print self.root_obj.data_df.columns[:]

    def remove_unused_vars(self, variable_to_plot, systs_read):
        """ remove variables and syst not needed for plotting before anything is read in. Bit clunky with the objects but it works and doesn't take ages """

        from syst_maps import syst_map, weight_systs

        #remove unused variables in data
        if ('mva' in variable_to_plot): used_variables = self.root_obj.train_vars + self.cut_map.keys() + ['dielectronPt', 'weight']
        else: used_variables = [variable_to_plot] + self.cut_map.keys() + ['dielectronPt', 'weight']

        #have to reset the used variable flag for all our attributes. Note that year dependent systs will be lost here depending on what first sample object is... but ok fine these are small anyway
        new_data_sample_objects = []
        for i in range(len(self.root_obj.data_objects)):
            i_obj = self.root_obj.data_objects[i]
            i_obj.vars_to_read = used_variables
            new_data_sample_objects.append(i_obj)
        self.root_obj.data_objects = new_data_sample_objects

        #now add syst and gen stuff and remove mc vars
        mc_used_variables =  used_variables[:] + ['genWeight', 'centralObjectWeight']

        for direction in ['Up', 'Down']:
            for syst_read in systs_read:
                if syst_read+direction in syst_map.keys():
                    mc_used_variables += [var_name+'_'+syst_read+direction for var_name in syst_map[syst_read+direction] if var_name in mc_used_variables]

        for weight_syst in weight_systs.keys():
            #if year in weight_systs[weight_syst]['years']: final_mc_vars += [weight_syst+ext for ext in weight_systs[weight_syst]['exts']]
            if weight_syst in systs_read:
                mc_used_variables += [weight_syst+ext for ext in weight_systs[weight_syst]['exts']]

        #have to reset the used variable flag for all our attributes. Note that year dependent systs will be lost here depending on what first sample object is... but ok fine these are small anyway
        new_bkg_sample_objects = []
        for i in range(len(self.root_obj.bkg_objects)):
            i_obj = self.root_obj.bkg_objects[i]
            i_obj.vars_to_read = mc_used_variables
            new_bkg_sample_objects.append(i_obj)
        self.root_obj.bkg_objects = new_bkg_sample_objects

    def pt_reweight(self):
        """
        Derive pt reweighting factors for the full applied preselection. Apply this to dfs 
        """

        print 'reweighting MC to Data in pT(Z) bins. '
        print 'DEBUG: cut map looks like: {}'.format(self.cut_map)
        #selection_str = [var_name+cut for var_name,cut in self.cut_map.iteritems() if cut != '']
        selection_str = []
        for var_name, cuts in self.cut_map.iteritems():
            if len(cuts)>1: selection_str += [var_name+cut for cut in cuts]
            else: selection_str.append(var_name+cuts[0])
        separator = ' and '
        all_selection = separator.join(selection_str)
        print 'DEBUG: final selection looks like: {}'.format(all_selection)

        #derive SFs
        year_to_scale_factors = {}
        for year in self.root_obj.years:
            presel_mc   = self.root_obj.mc_df_bkg.query(all_selection+' and year=="{}"'.format(year))
            print 'presel string:'
            print all_selection+" and year=={}".format(year)
            print 'DEBUG presel mc:'.format(presel_mc[:10])
            presel_data = self.root_obj.data_df.query(all_selection+' and year=="{}"'.format(year))
            print 'DEBUG presel mc:'.format(presel_data[:10])
            dy_mc_pt    = presel_mc['dielectronPt'].values
            dy_w        = presel_mc['weight'].values
            dy_data_pt  = presel_data['dielectronPt'].values

            del presel_mc
            del presel_data
                
            pt_bins = np.linspace(0,400,61) #VBF
            #pt_bins = np.linspace(0,180,101) #ggH
            mc_pt_summed, _ = np.histogram(dy_mc_pt, bins=pt_bins, weights=dy_w)
            data_pt_summed, bin_edges = np.histogram(dy_data_pt, bins=pt_bins)
            year_to_scale_factors[year] = data_pt_summed/mc_pt_summed

        print 'DEBUG: year : pT rew scale factors are:'
        print year_to_scale_factors
        print 'DEBUG: bin edges'
        print bin_edges
            
        scaled_dfs = []
        for year in self.root_obj.years:
            df_year_i = self.root_obj.mc_df_bkg.query(self.root_obj.cut_string+'and year=="{}"'.format(year))
            scale_factors = year_to_scale_factors[year]
            for i_bin in range(len(scale_factors)-1):
                temp_df = df_year_i[df_year_i.dielectronPt > bin_edges[i_bin]] 
                temp_df = temp_df[temp_df.dielectronPt < bin_edges[i_bin+1]] 
                #temp_df['weight'] *= scale_factors[i_bin]
                temp_df['pt_weight'] = temp_df['weight'].copy() * scale_factors[i_bin]
                scaled_dfs.append(temp_df)  
                print 'DEBUG: for pT bin: {} to {}, applying SF of {}'.format(bin_edges[i_bin],bin_edges[i_bin+1], scale_factors[i_bin])
 
            the_rest = self.root_obj.mc_df_bkg[self.root_obj.mc_df_bkg.dielectronPt > bin_edges[-1]]
            the_rest['pt_weight'] = the_rest['weight']
            scaled_dfs.append(the_rest)
              
        self.root_obj.mc_df_bkg = pd.concat(scaled_dfs, ignore_index=True)
        del scaled_dfs

        print 'DEBUG: sumW Data: {}'.format(np.sum(self.root_obj.data_df.query(all_selection)['weight']))
        print 'DEBUG: sumW background after pT reweighting: {}'.format(np.sum(self.root_obj.mc_df_bkg.query(all_selection)['weight']))
 
        for year in self.root_obj.years:
            self.root_obj.save_modified_dfs(year, ignore_sig=True)

       

    def manage_dtypes(self, systematics, save=False, syst_types=['Up','Down']):
        """
        Change data types to remove precision (and memory use) where possible.
        """

        from syst_maps import syst_map 

        f32_precision_vars = ['leadElectronPtOvM','subleadElectronPtOvM','leadElectronEta','subleadElectronEta',
                              'dielectronCosPhi', 'dielectronPt', 'dielectronMass', 'leadJetPt', 'subleadJetPt',
                              'leadJetEn', 'leadJetEta', 'leadJetPhi', 'leadJetQGL',
                              'subleadJetEn', 'subleadJetEta', 'subleadJetPhi', 'subleadJetQGL',
                              'subsubleadJetEn', 'subsubleadJetEta', 'subsubleadJetPhi', 'subsubleadJetQGL',
                              'dijetAbsDEta', 'dijetMass', 'dijetDieleAbsDEta', 'dijetDieleAbsDPhiTrunc',
                              'dijetMinDRJetEle', 'dijetCentrality', 'dijetDPhi', 'leadJetDieleDPhi', 'leadJetDieleDEta',
                              'subleadJetDieleDPhi', 'subleadJetDieleDEta' 
                             ]
        i8_precision_vars  = ['leadElectronCharge', 'subleadElectronCharge '] 

        #get syst variations
        f32_syst_vars = []
        i8_syst_vars  = []
        for syst_name in systematics:
            for ext in syst_types:
                f32_syst_vars += [var_name+'_'+syst_name+ext for var_name in f32_precision_vars] 
                i8_syst_vars  += [var_name+'_'+syst_name+ext for var_name in i8_precision_vars] 

        #change certain dtypes in remaining variables
        for v in f32_precision_vars+f32_syst_vars:
            if v in self.root_obj.mc_df_bkg.columns:
                self.root_obj.mc_df_bkg[v] = self.root_obj.mc_df_bkg[v].astype('float16')
            if v in self.root_obj.data_df.columns:
                self.root_obj.data_df[v]   = self.root_obj.data_df[v].astype('float16')

        for v in i8_precision_vars+i8_syst_vars:
            if v in self.root_obj.mc_df_bkg.columns:
                self.root_obj.mc_df_bkg[v] = self.root_obj.mc_df_bkg[v].astype('int8')
            if v in self.root_obj.data_df.columns:
                self.root_obj.data_df[v]   = self.root_obj.data_df[v].astype('int8')

        #save df's with new data types
        if save:
            for year in self.root_obj.years:
                self.root_obj.save_modified_dfs(year, ignore_sig=True)
          

    def plot_data(self, cut_string, axes, variable, bins):
        """ Plot the data """

        cut_df             = self.root_obj.data_df.query(cut_string)
        var_to_plot        = cut_df[variable].values
        var_weights        = cut_df['weight'].values
        del cut_df

        data_binned, bin_edges = np.histogram(var_to_plot, bins=bins, weights=var_weights)
        print '--> Integral of hist: {}, for data is: {}'.format(variable,np.sum(data_binned))
        bin_centres = (bin_edges[:-1] + bin_edges[1:])/2
        data_stat_down, data_stat_up = self.poisson_interval(data_binned, data_binned)

        #FIXME: sort this niche issue out
        #dataUp[dataUp==np.inf] == 0

        data_no_zeros = data_binned.copy() 
        data_no_zeros[data_no_zeros==0] = np.nan #removes markers at zero i.e. no entries

        axes[0].errorbar(bin_centres, data_no_zeros, 
                         yerr=[data_binned-data_stat_down, data_stat_up-data_binned],
                         label='Data', fmt='o', ms=4, color='black', capsize=0)

        return data_binned, bin_centres, (data_stat_down, data_stat_up)

    def plot_bkgs(self, cut_string, axes, variable, bins, data_binned, bin_centres, data_stat_down_up):
        """ 
        Nominal MC hist and stat errors should be constructed with pT rew weights.
        Keep a set of MC sumw's for comparison to systs as wekl
        """

       
        bkg_frame = self.root_obj.mc_df_bkg.query(cut_string)
        print 'DEBUG: bkg sumW nominal after nominal presel: {}'.format(np.sum(bkg_frame['weight']))

        #get norm factor
        var_to_plot_all_bkgs  = bkg_frame[variable].values
        var_weights_all_bkgs  = bkg_frame['pt_weight'].values 
        sumw_all_bkgs, _      = np.histogram(var_to_plot_all_bkgs, bins=bins, weights=var_weights_all_bkgs)
        self.k_factor         = np.sum(data_binned)/np.sum(sumw_all_bkgs)
        sumw_all_bkgs        *= self.k_factor #NOTE: still need this for ggH since nominal phase space which SFs are dervied in, is different to phase space of variables requiring > 0J! So norm will be off in those

        #Set up stat unc arrays to add to
        stat_down_all_bkgs = np.zeros(len(bins)-1)
        stat_up_all_bkgs   = np.zeros(len(bins)-1)

        #plot each proc and add up stat uncertainties
        for counter, bkg_proc in enumerate(self.root_obj.bkg_procs):
            proc_frame            = bkg_frame[bkg_frame.proc==bkg_proc]
            var_to_plot           = proc_frame[variable].values
            var_no_pt_rew_weights = proc_frame['weight'].values 
            var_weights           = proc_frame['pt_weight'].values 
            del proc_frame

            var_weights          *= self.k_factor #NOTE: see above note. This is only for plotting and MC stat errors, not syst evaluation, as is the case with all reweightings
            sumw, _               = np.histogram(var_to_plot, bins=bins, weights=var_weights)
            #self.mc_totals_pt_re[bkg_proc]  = sumw
            sumw2, _              = np.histogram(var_to_plot, bins=bins, weights=var_weights**2)
            stat_down, stat_up    = self.poisson_interval(sumw, sumw2)
            stat_down_all_bkgs    += stat_down
            stat_up_all_bkgs      += stat_up
            print '--> Integral of hist: {}, for background proc {} is: {}'.format(variable, bkg_proc, np.sum(sumw))
            axes[0].hist(var_to_plot, bins=bins, label=bkg_proc, weights=var_weights, color=self.colours[counter], histtype='stepfilled')

            #for syst stuff later on:
            no_pt_rew_sumw, _                      = np.histogram(var_to_plot, bins=bins, weights=var_no_pt_rew_weights)
            self.mc_totals_no_pt_rew[bkg_proc] = no_pt_rew_sumw

        self.mc_stat_unc          = [sumw_all_bkgs-stat_down_all_bkgs, stat_up_all_bkgs-sumw_all_bkgs]
        self.mc_total             = sumw_all_bkgs

        data_bkg_ratio   = data_binned/sumw_all_bkgs
        axes[1].errorbar( bin_centres, data_bkg_ratio, yerr=[(data_binned-data_stat_down_up[0])/sumw_all_bkgs,(data_stat_down_up[1] - data_binned)/sumw_all_bkgs], fmt='o', ms=4, color='black', capsize=0, zorder=3)


    def plot_systematics(self, cut_string, axes, variable, bins, systematics, do_mva=True):
        """ self explanatory """
        
        from syst_maps import weight_systs

        #create and fill one Systematic object info for each syst FIXME FIXME (for each sample?)
        syst_objects = {}
        for syst_name in systematics:
            if syst_name in weight_systs.keys(): syst_dfs = self.get_weight_syst(syst_name, cut_string, plot_var=variable, do_mva=do_mva)
            else: syst_dfs = self.relabel_syst_vars(syst_name, cut_string, plot_var=variable)
            #print 'DEBUG: nominal vars '
            #print self.root_obj.mc_df_bkg['dielectronPt']
            #print 'DEBUG: syst up vars '
            #print syst_dfs['Up']['dielectronPt']
            #print 'DEBUG: syst down vars '
            #print syst_dfs['Down']['dielectronPt']
            for syst_type in syst_dfs.keys():
                #syst_dfs[syst_type]['weight'] = syst_dfs[syst_type]['weight'].copy() * self.k_factor #FIXME can remove this
                #syst_dfs[syst_type]['weight'] *= self.k_factor #FIXME check can remove the copy() #FIXME
                if do_mva: syst_dfs[syst_type][self.proc+'_mva'] = self.eval_bdt(self.clf, syst_dfs[syst_type], self.root_obj.train_vars)
            syst_objects[syst_name] = Systematic(syst_name, down_frame=syst_dfs['Down'], up_frame=syst_dfs['Up'])
            #print 'DEBUG: for syst: {}, MVA up/down diff are equal: {} !!'.format(syst_name, np.array_equal(syst_dfs['Up'][self.proc+'_mva'],syst_dfs['Down'][self.proc+'_mva']))
            #print 'DEBUG: for syst: {}, leadJetEn up/down diff are equal: {} !!'.format(syst_name, np.array_equal(syst_dfs['Up']['leadJetEn'],syst_dfs['Down']['leadJetEn']))
            #if do_mva: print 'DEBUG: for syst: {}, leadPtOvM up/down diff are equal: {} !!'.format(syst_name, np.array_equal(syst_dfs['Up']['leadElectronPtOvM'],syst_dfs['Down']['leadElectronPtOvM']))
            del syst_dfs
            
        for syst_name, syst_obj in syst_objects.iteritems():
            print 'DEBUG: sys name: {}'.format(syst_name)
            for syst_type, i_frame in syst_obj.up_down_frames.iteritems():
                for bkg_proc in self.root_obj.bkg_procs:
                    proc_frame       = i_frame[i_frame.proc==bkg_proc]
                    print 'DEBUG: syst frame columns {}'.format(proc_frame.columns[:])
                    var_to_plot      = proc_frame[variable].values
                    weight           = proc_frame['weight'].values #will be shifted by weight syst if reading those in
                    i_syst_binned, _ = np.histogram(var_to_plot, bins=bins, weights=weight)
                    print 'HONK PART 2:'
                    print 'shifted weight'
                    print weight
                    print 'variable:'
                    print var_to_plot
                    print 'nomainal variable:'
                    print self.root_obj.mc_df_bkg.query(cut_string)[variable]
 
                    #compare variation to the nominal for given sample and fill bin list
                    true_down_variations  = []
                    true_up_variations    = []
 
                    print 'bkg proc: {}'.format(bkg_proc)
                    print 'syst type: {}'.format(syst_type)
                    print 'i_syst binned:'
                    print i_syst_binned
                    print 'mc total for proc'
                    print  self.mc_totals_no_pt_rew[bkg_proc]
                    #compare the systematic change to the !nominal! bin entries for that proc.
                    for ybin_syst, ybin_nominal in zip(i_syst_binned, self.mc_totals_no_pt_rew[bkg_proc]):
                      if ybin_syst > ybin_nominal: 
                        true_up_variations.append(ybin_syst - ybin_nominal)
                        true_down_variations.append(0)
                      elif ybin_syst < ybin_nominal:
                        true_down_variations.append(ybin_nominal - ybin_syst)
                        true_up_variations.append(0)
                      else: #sometimes in low stat cases we get no change either way wrt nominal
                        true_up_variations.append(0)
                        true_down_variations.append(0)

                    print 'true down variations'
                    print true_down_variations
                    print 'true up variations'
                    print true_up_variations
 
                    if syst_type=='Down':
                        syst_obj.down_syst_binned[bkg_proc] = [np.asarray(true_down_variations), 
                                                               np.asarray(true_up_variations)]
                    else:
                        syst_obj.up_syst_binned[bkg_proc]   = [np.asarray(true_down_variations), 
                                                               np.asarray(true_up_variations)]

        #add all the up/down variations (separately) for each systematic in quadrature for each bin, 
        #for each proc 

        down_squares = [] 
        up_squares   = [] 

        for syst_name, syst_obj in syst_objects.iteritems():
            for bkg_proc in self.root_obj.bkg_procs:
                down_squares.append( syst_obj.down_syst_binned[bkg_proc][0]**2 )
                down_squares.append( syst_obj.up_syst_binned[bkg_proc][0]**2 )

                up_squares.append( syst_obj.down_syst_binned[bkg_proc][1]**2 )
                up_squares.append( syst_obj.up_syst_binned[bkg_proc][1]**2 )

        #print 'down squares'
        #print down_squares
        #print 'up squares'
        #print up_squares

        #now add up each bin that has been squared (will add element wise since np array)
        syst_merged_downs = np.zeros(len(bins)-1)
        syst_merged_ups   = np.zeros(len(bins)-1)

        for down_array in down_squares:
            syst_merged_downs += down_array
        for up_array in up_squares:
            syst_merged_ups   += up_array


        #combined with correpsonding stat error. note that if we are considering a sample set, the name and set attributes are identical now
        #NOTE: syst have already been squared above in prep for this step!

        #syst_merged_downs = np.sqrt( syst_merged_downs + self.mc_stat_uncs[sample_obj.name][0]**2) 
        #syst_merged_ups   = np.sqrt( syst_merged_ups   + self.mc_stat_uncs[sample_obj.name][1]**2) 

        #merged_syst_obj.merged_syst_stat_down  = syst_merged_downs
        #merged_syst_obj.merged_syst_stat_up    = syst_merged_ups

        #merged_downs = sample_obj.systematics['merged_systs'].merged_syst_stat_down
        #merged_ups   = sample_obj.systematics['merged_systs'].merged_syst_stat_up

        #FIXME add back in!
        merged_downs = np.sqrt( syst_merged_downs + self.mc_stat_unc[0]**2) 
        merged_ups   = np.sqrt( syst_merged_ups   + self.mc_stat_unc[1]**2) 

        #FIXME syst only
        #merged_downs = np.sqrt( syst_merged_downs) 
        #merged_ups   = np.sqrt( syst_merged_ups  ) 

        #FIXME stat only
        #merged_downs = np.sqrt( self.mc_stat_unc[0]**2) 
        #merged_ups   = np.sqrt( self.mc_stat_unc[1]**2) 

        print 'mc total'
        print self.mc_total
        print 'syst downs'
        print np.sqrt(syst_merged_downs)
        print 'syst ups'
        print np.sqrt(syst_merged_ups)
        print 'mc stat down: {}'.format(self.mc_stat_unc[0])
        print 'mc stat up: {}'.format(self.mc_stat_unc[1])

        up_yield   = self.mc_total + merged_ups
        #FIXME: fix this niche issue below with poiss err function
        up_yield[up_yield==np.inf] = 0
        down_yield = self.mc_total - merged_downs

        print 'up yield final: {}'.format(up_yield)
        print 'down yield final: {}'.format(down_yield)

        axes[0].fill_between(bins, list(down_yield)+[down_yield[-1]], list(up_yield)+[up_yield[-1]], alpha=0.3, step="post", color="lightcoral", lw=1, edgecolor='red', zorder=4, label='Simulation stat. $\oplus$ syst. unc.')
        axes[0].set_ylim(bottom=0)

        #total_mc             = self.mc_total
        sigma_tot_ratio_down = merged_downs/self.mc_total
        sigma_tot_ratio_up   = merged_ups/self.mc_total
                
        ratio_down_excess    = np.ones(len(self.mc_total)) - sigma_tot_ratio_down
        ratio_up_excess      = np.ones(len(self.mc_total)) + sigma_tot_ratio_up
                
        #1. if we have no entries, the upper limit is inf and lower is nan
        #2. hence we set both to nan, so they aren't plot in the ratio plot
        #3  BUT if we have [nan, nan, 1 ,2 ,,, ] and/or [1, 2, ... nan, nan] 
        #   i.e. multiple Nan's at each end, then we have to set to Nan closest
        #   to the filled numbers to 1, such that error on the closest filled value
        #   doesn't mysteriously disappear
        #EDIT: gave up and did this dumb fix:

        #print ratio_up_excess
        #print ratio_down_excess
        #ratio_up_excess[ratio_up_excess==np.inf] = 1 
        #ratio_down_excess = np.nan_to_num(ratio_down_excess)
        #ratio_down_excess[ratio_down_excess==0] =1
        
        axes[1].fill_between(bins, list(ratio_down_excess)+[ratio_down_excess[-1]], list(ratio_up_excess)+[ratio_up_excess[-1]] , alpha=0.3, step="post", color="lightcoral", lw=1 , zorder=2)
        axes[1].set_ylabel('Data/MC', size=13)


    def relabel_syst_vars(self, syst_name, cut_string, plot_var, syst_types=['Up','Down']):
        """  
        Overwrite the nominal branches, with the analagous branch but with a systematic variation.
        For example if syst = jec, we may overwrite "leadJetPt" with "leadJetPt_JecUp/Down"
        Arguments
        ---------
        """  
             
        #import variables that may change with each systematic
        from syst_maps import syst_map

        syst_dfs = {}
        print '\n\n'
        print 'DEBUG: reading systematic: {}'.format(syst_name)
        for ext in syst_types:
            print 'DEBUG: reading ext: {}'.format(ext)
            nominal_vars = syst_map[syst_name+ext]
            replacement_vars = [var_name+'_'+syst_name+ext for var_name in syst_map[syst_name+ext]] 

            #need to remove events asap else memory kills jobs. Hence apply preselection to syst vars before doing renaming stuff
            syst_cut_map = self.cut_map.copy()
            counter = 0
            print 'DEBUG: nominal cut map: {}'.format(self.cut_map)
	    print 'DEBUG: nominal vars: {}'.format(nominal_vars)
            print 'DEBUG: replacement vars: {}'.format(replacement_vars)

            #delete plot var from cut map (dont want to cut on variable we are plotting)
            if plot_var in syst_cut_map.keys(): del syst_cut_map[plot_var] 

            #replace nominal vars in the cut map with syst vars
            for var in nominal_vars:
                if var in syst_cut_map.keys():
                    print 'DEBUG: changing cut_var from {} to {}'.format(var, replacement_vars[counter])
                    del syst_cut_map[var]
                    syst_cut_map[replacement_vars[counter]] = self.cut_map[var] #if cut has syst variation for syst being considered. Format is syst_varies_name : cut (same as nominal)
                counter+=1
            print 'DEBUG: syst varied ({}) cut map: {}'.format(ext,syst_cut_map)

            #syst_cut_list = [var_name+cut for var_name,cut in syst_cut_map.iteritems()]
            syst_cut_list = []
            for var_name, cuts in syst_cut_map.iteritems():
                if len(cuts)>1: syst_cut_list += [var_name+cut for cut in cuts]
                else: syst_cut_list.append(var_name+cuts[0])
            syst_cut_string = ' and '.join(syst_cut_list)
            print 'DEBUG syst {} df sumW before cuts: {}'.format(ext, np.sum(self.root_obj.mc_df_bkg['weight']))
            df_copy = self.root_obj.mc_df_bkg.query(syst_cut_string)
             
            #relabel. Delete nominal column frst else pandas throws an exception. Then rename syst col name -> nominal col name
            for n_var, replacement_var in zip(nominal_vars,replacement_vars):
                #print 'replacing syst title: {} with nominal title: {}'.format(replacement_var, n_var)
                if n_var in df_copy.columns:
                    del df_copy[n_var]
                    #df_copy.drop(labels=n_var, inplace=True)
                    df_copy.rename(columns={replacement_var : n_var}, inplace=True) #wont always be in col since removed unused vars!  
                    print 'DEBUG: changing: {} and {}'.format(replacement_var, n_var)
            syst_dfs[ext] = df_copy
            print 'DEBUG syst {} df sumW after cuts: {}'.format(ext, np.sum(df_copy['weight']))
            #print 'DEBUG: for syst: {}, after cuts, nominal and {} diff are equal: {} !!'.format(syst_name, ext, np.array_equal(df_copy['leadJetEn'],self.root_obj.mc_df_bkg['leadJetEn']))
        return syst_dfs

    def get_weight_syst(self, syst_name, cut_string, plot_var, syst_types=['Up','Down'], do_mva=True):
        """
        Compute the weight systematics and for up(down) syst return a df of the plot var, and up(down) varied weights, making sure to overwrite the nominal weight branch
        """ 
        from syst_maps import weight_systs

        #create one df for each up/down variation
        syst_dfs = {}
        for ext in syst_types:
            if do_mva: 
                train_vars_minus_plot_var = [v for v in self.root_obj.train_vars if v!=plot_var] #protect against usual case where plot var is contained in training variable set
                cut_vars += [v for v in self.cut_map.keys() if (v not in (train_vars_minus_plot_var+plot_var))]
                final_vars = cut_vars + train_vars_minus_plot_var
                syst_dfs[ext] = self.root_obj.mc_df_bkg[[plot_var]+['proc']+final_vars] 
            else: 
                final_vars = [v for v in self.cut_map.keys() if v!=plot_var]
                syst_dfs[ext] = self.root_obj.mc_df_bkg[[plot_var,'proc']+final_vars]
                

        #compute the weigth variations and add them to df
        down_tag, nom_tag, up_tag = weight_systs[syst_name]['exts'][0], weight_systs[syst_name]['exts'][1], weight_systs[syst_name]['exts'][2]
        syst_dfs['Up']['weight']   = (self.root_obj.mc_df_bkg['{}{}'.format(syst_name,up_tag)] / self.root_obj.mc_df_bkg['{}{}'.format(syst_name,nom_tag)]) * self.root_obj.mc_df_bkg['weight'].copy()
        syst_dfs['Down']['weight'] = (self.root_obj.mc_df_bkg['{}{}'.format(syst_name,down_tag)] / self.root_obj.mc_df_bkg['{}{}'.format(syst_name,nom_tag)]) * self.root_obj.mc_df_bkg['weight'].copy()

        print 'HONK: CUT STRING (should be full list of compiled cuts in this function)'
        print cut_string
        print 'End of HONK'

        syst_dfs['Up'].query(cut_string, inplace=True)
        syst_dfs['Down'].query(cut_string, inplace=True)


        return syst_dfs


    def eval_mva(self, mva_config, output_tag):
        """ 
        evaluate score on whatever mva is passed, on whatever df is passed. Not used at the moment.
        """

        #FIXME fix DNN eval

        with open(mva_config, 'r') as mva_config_file:
            config            = yaml.load(mva_config_file)
            proc_to_model     = config['models']
            for proc, model in proc_to_model.iteritems():
                if proc not in output_tag: continue

                #for BDT - proc:[var list]. For DNN - proc:{var_type1:[var_list_type1], var_type2: [...], ...}
                if isinstance(model,dict):
                    object_vars     = proc_to_train_vars[proc]['object_vars']
                    flat_obj_vars   = [var for i_object in object_vars for var in i_object]
                    event_vars      = proc_to_train_vars[proc]['event_vars']
 
                    dnn_loaded = tag_obj.load_dnn(proc, model)
                    train_tag = model['architecture'].split('_model')[0]
                    tag_obj.eval_lstm(dnn_loaded, train_tag, root_obj, proc, object_vars, flat_obj_vars, event_vars)
 
                elif isinstance(model,str): 
                    clf = pickle.load(open('models/{}'.format(model), "rb"))
                    self.root_obj.mc_df_bkg[proc+'_mva'] = self.eval_bdt(clf, self.root_obj.mc_df_bkg, self.root_obj.train_vars)
                    self.root_obj.data_df[proc+'_mva'] =  self.eval_bdt(clf, self.root_obj.data_df, self.root_obj.train_vars)
                    self.clf = clf
                    self.proc = proc
                else: raise IOError('Did not get a classifier models in correct format in config')


    def eval_bdt(self, clf, df, train_vars):
        """ 
        evaluate score for BDT, on whatever df is passed
        """
        return clf.predict_proba(df[train_vars].values)[:,1:].ravel()   

    @classmethod
    def set_canv_style(self, axes, variable, bins, label='Work in progress', energy='13 TeV'):
        x_err = abs(bins[-1] - bins[-2])
        axes[0].set_ylabel('Events / {0:.2g}'.format(2*x_err) , size=14, ha='right', y=1)
        #if variable.norm: axes[0].set_ylabel('1/N dN/d(%s) /%.2f' % (variable.xlabel,x_err, ha='right', y=1)
        axes[0].text(0, 1.01, r'\textbf{CMS} %s'%label, ha='left', va='bottom', transform=axes[0].transAxes, size=14)
        axes[0].text(1, 1.01, r'138 fb\textsuperscript{-1} (%s)'%(energy), ha='right', va='bottom', transform=axes[0].transAxes, size=14)
        #axes[0].text(1, 1.01, r'59.7 fb\textsuperscript{-1} (%s)'%(energy), ha='right', va='bottom', transform=axes[0].transAxes, size=14)
        #axes[0].text(1, 1.01, r'41.5 fb\textsuperscript{-1} (%s)'%(energy), ha='right', va='bottom', transform=axes[0].transAxes, size=14)
        #axes[0].text(1, 1.01, r'35.9 fb\textsuperscript{-1} (%s)'%(energy), ha='right', va='bottom', transform=axes[0].transAxes, size=14)
        #axes[0].text(1, 1.01, r'(%s)'%(energy), ha='right', va='bottom', transform=axes[0].transAxes, size=14)
       
        axes[1].set_ylim(0.52,1.48)
        axes[1].grid(True, linestyle='dotted')

        current_bottom, current_top = axes[0].get_ylim()
        #axes[0].set_ylim(top=current_top*1.45)
        axes[0].set_ylim(top=current_top*1.4)

        return axes

    def get_cut_string(self, var_to_plot):
        """
           Form a string of cuts to query samples. Take care to remove
           the cuts on the variable being plot
        """

        cut_dict = self.cut_map.copy()
        print 'cut dict is {}:'.format(cut_dict)
        if var_to_plot in cut_dict.keys(): del cut_dict[var_to_plot]
        #cut_list_non_null = [var_name+cut for var_name,cut in cut_dict.iteritems() if cut != '']
        cut_list_non_null = []
        for var_name, cuts in cut_dict.iteritems():
            if len(cuts)>1: cut_list_non_null += [var_name+cut for cut in cuts]
            else: cut_list_non_null.append(var_name+cuts[0])
        separator = ' and '
        cut_string = separator.join(cut_list_non_null)
        print 'cut string is {}:'.format(cut_string)
        return cut_string

    def poisson_interval(self, x, variance, level=0.68): #FIXME: dont copy, take this from PlottingUtils class
        neff = x**2/variance
        scale = x/neff
     
        # CMS statcomm recommendation
        l = scipy.stats.gamma.interval(
            level, neff, scale=scale,
        )[0]
        u = scipy.stats.gamma.interval(
            level, neff+1, scale=scale
        )[1]
     
        # protect against no effecitve entries
        l[neff==0] = 0.
     
        # protect against no variance
        l[variance==0.] = 0.
        u[variance==0.] = np.inf
        return l, u

class Systematic(object):
    """ 
       Object containing attributes related to systematic variations.
       One object is created per systematic uncertainty, for all bkg processes inclusively.
    """ 
        
    def __init__(self, name, up_frame=None, down_frame=None):
            self.name                  = name
            self.up_down_frames        = {'Up':up_frame, 'Down':down_frame}
            self.up_syst_binned        = {} #{proc1: [true_downs, true_ups], proc2: ...}
            self.down_syst_binned      = {} #{proc1: [true_downs, true_ups], proc2: ...}
            self.true_up               = {}
            self.true_down             = {}
