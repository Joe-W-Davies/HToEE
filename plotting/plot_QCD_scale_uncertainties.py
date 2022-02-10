import argparse
import numpy as np
import yaml
import pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
try:
     plt.style.use("cms10_6_HP")
except IOError:
     import warnings
     warnings.warn('Could not import user defined matplot style file. Using default style settings...')

from DataHandling import ROOTHelpers
from PlottingUtils import Plotter

def main(options):

    #take options from the yaml config
    with open(options.config, 'r') as config_file:
        config            = yaml.load(config_file)
        output_tag        = config['output_tag'] + 'with_QCD_scales'
        mH                = config['mH']

        mc_dir            = config['mc_file_dir']
        mc_fnames         = config['mc_file_names']
  
        #data not needed yet, could use this for validation later. keep for compat with class
        data_dir          = config['data_file_dir']
        data_fnames       = config['data_file_names']

        train_vars        = config['train_vars'] 
        vars_to_add       = config['vars_to_add']
        presel            = config['preselection']

        proc_to_tree_name = config['proc_to_tree_name']

        sig_colour        = 'forestgreen'
 
                                           #Data handling stuff#

        #load the mc dataframe for all years
        root_obj = ROOTHelpers(output_tag, mc_dir, mc_fnames, data_dir, data_fnames, proc_to_tree_name, train_vars, vars_to_add, presel, mH=mH)

        for sig_obj in root_obj.sig_objects:
            root_obj.load_mc(sig_obj, reload_samples=options.reload_samples, read_QCD_arrays=True)
        root_obj.concat()

        #set of up some hard coded variables...
        #pt_bins      = np.linspace(0,400,61) #VBF
        #pt_bins = np.linspace(0,180,101) #ggH
        pt_bins = np.linspace(0,180,51) #ggH testing less grnaular binning
        bin_centres  = (pt_bins[:-1] + pt_bins[1:])/2

        qcd_indexes   = [0,1,3,5,7,8]
        qcd_var_names = ['qcd_scale_variation_'+str(v) for v in qcd_indexes]
        variation_map = {0:8, 1:7, 3:5}
        colour_map =    {0:'red', 1:'blue', 3:'green'}
        QCD_var_name_map = {0:'Both up/down', 1:'Renorm up/down', 3:'Fact up/down'}
        qcd_index_to_binned_pt = {}

        #read in SFs for each year
        with open(options.sfs_dict, 'r') as sfs_dict:
            sfs_per_year    = yaml.load(sfs_dict)

        #now plot eveything
        for year in sfs_per_year.keys():
            print year
            #sig_df = root_obj.mc_df_sig.query("year=={}".format(year))
            sig_df = root_obj.mc_df_sig.query("year==2016A")

            for qcd_var_name,idv in zip(qcd_var_names,qcd_indexes):
                shifted_sum_w, bin_edges = np.histogram(sig_df['dielectronPt'], weights=sig_df[qcd_var_name]*sig_df['weight'], bins=pt_bins)
                nominal_sum_w, _         = np.histogram(sig_df['dielectronPt'], weights=sig_df['weight'], bins=pt_bins)
                qcd_index_to_binned_pt[idv] = shifted_sum_w/nominal_sum_w

            fig = plt.figure(1)
            axis = fig.gca()

            #style 1
            #for up, down in variation_map.iteritems():
            #    up_binned = qcd_index_to_binned_pt[up]
            #    down_binned = qcd_index_to_binned_pt[down]
            #    axis.fill_between(pt_bins, list(up_binned)+[up_binned[-1]], list(down_binned)+[down_binned[-1]], alpha=0.2, step="post", lw=1, color=colour_map[up], label=QCD_var_name_map[up])

            #style 2
            for up, down in variation_map.iteritems():
                up_binned = qcd_index_to_binned_pt[up]
                down_binned = qcd_index_to_binned_pt[down]
                axis.hist(pt_bins[:-1], bins=pt_bins, weights=up_binned, histtype='step', lw=1, color=colour_map[up])
                axis.hist(pt_bins[:-1], bins=pt_bins, weights=down_binned, histtype='step', lw=1, color=colour_map[up], label=QCD_var_name_map[up])
            stacked_sumw_s = np.stack(qcd_index_to_binned_pt.values())
            upper_env = []
            lower_env = []
            for i_sumw in range(len(shifted_sum_w)):
                col =  stacked_sumw_s.T[i_sumw]
                upper_env.append(np.max(col))
                lower_env.append(np.min(col))
            axis.fill_between(pt_bins, list(upper_env)+[upper_env[-1]], list(lower_env)+[lower_env[-1]], alpha=0.2, step="post", lw=1, color='grey', label='Variation envelope')

            axis.errorbar(bin_centres, sfs_per_year[year], 
                             xerr=(pt_bins[0]+pt_bins[1])/2,
                             label='$p_{T}(ee)$ SFs', fmt='o', ms=3, color='black', capsize=0)
            axis.legend(bbox_to_anchor=(0.95,0.95), ncol=2)
            axis.set_xlabel('$p_{T}(ee)$', ha='right', x=1, size=13)
            axis.text(0, 1.01, r'\textbf{CMS} Work in progress', ha='left', va='bottom', transform=axis.transAxes, size=14)
            axis.text(1, 1.01, r'41.5 fb\textsuperscript{-1} (13 TeV)', ha='right', va='bottom', transform=axis.transAxes, size=14)
            axis.set_ylim(bottom=0.65, top=1.6)
            axis.set_xlim(left=0, right=pt_bins[-1])
            
            fig.savefig('{}.pdf'.format(year))
            plt.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group('Required Arguments')
    required_args.add_argument('-c','--config', action='store', required=True)
    required_args.add_argument('-S','--sfs_dict', action='store', required=True)
    opt_args = parser.add_argument_group('Optional Arguements')
    opt_args.add_argument('-r','--reload_samples', action='store_true', default=False)
    options=parser.parse_args()
    main(options)
