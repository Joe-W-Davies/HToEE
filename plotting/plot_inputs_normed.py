import argparse
import numpy as np
import yaml
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
try:
     plt.style.use("cms10_6_HP")
except IOError:
     warnings.warn('Could not import user defined matplot style file. Using default style settings...')
import scipy.stats

from DataHandling import ROOTHelpers
from PlottingUtils import Plotter
from Utils import Utils

def main(options):

    #take options from the yaml config
    with open(options.config, 'r') as config_file:
        config            = yaml.load(config_file)
        output_tag        = config['output_tag']
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
        #sig_colour        = 'red'
        bkg_colour        = 'violet'
 
                                           #Data handling stuff#

        #load the mc dataframe for all years
        if options.pt_reweight: 
            cr_selection = config['reweight_cr']
            output_tag += '_pt_reweighted'
            root_obj = ROOTHelpers(output_tag, mc_dir, mc_fnames, data_dir, data_fnames, proc_to_tree_name, train_vars, vars_to_add, cr_selection, mH=mH)
        else: root_obj = ROOTHelpers(output_tag, mc_dir, mc_fnames, data_dir, data_fnames, proc_to_tree_name, train_vars, vars_to_add, presel, mH=mH)

        for sig_obj in root_obj.sig_objects:
            root_obj.load_mc(sig_obj, reload_samples=options.reload_samples)
        for bkg_obj in root_obj.bkg_objects:
            root_obj.load_mc(bkg_obj, bkg=True, reload_samples=options.reload_samples)
        root_obj.concat()

        if options.pt_reweight and options.reload_samples: 
            for year in root_obj.years:
                root_obj.pt_reweight('DYMC', year, presel)

        #root_obj.add_LabEleDieleDTheta()
        #root_obj.encode_n_jets()
                                            #Plotter stuff#

        #set up X, w and y, train-test 
        plotter = Plotter(root_obj, train_vars, sig_col=sig_colour, norm_to_data=True)
        for var in train_vars:

            fig  = plt.figure(1)
            axes = fig.gca()

            var_sig     = root_obj.mc_df_sig[var].values
            sig_weights = root_obj.mc_df_sig['weight'].values
            var_bkg     = root_obj.mc_df_bkg[var].values
            bkg_weights = root_obj.mc_df_bkg['weight'].values

            bins = np.linspace(plotter.var_to_xrange[var][0], plotter.var_to_xrange[var][1], options.n_bins)

            #add sig mc
            axes.hist(var_sig, bins=bins, label=plotter.sig_labels[0]+r' ($\mathrm{H}\rightarrow\mathrm{ee}$)', weights=sig_weights, histtype='stepfilled', color='red', zorder=10, alpha=0.4, normed=True)
            axes.hist(var_bkg, bins=bins, label='Simulated background', weights=bkg_weights, histtype='stepfilled', color='blue', zorder=0, alpha=0.4, normed=True)

            axes.set_ylabel('Arbitrary Units', ha='right', y=1, size=13)
            current_bottom, current_top = axes.get_ylim()
            if not plotter.var_to_xrange[var][2]: axes.set_ylim(bottom=0, top=1.2*current_top)
            else:
                axes.set_yscale('log', nonposy='clip')
                axes.set_ylim(bottom=0.01, top=5*current_top)

            axes.set_xlim(left=plotter.var_to_xrange[var][0], right=plotter.var_to_xrange[var][1])

            axes.legend(bbox_to_anchor=(0.97,0.97), ncol=1)
            plotter.plot_cms_labels(axes, lumi='')
               
            axes.set_xlabel('{}'.format(plotter.var_to_xstring[var]), ha='right', x=1, size=13)

            Utils.check_dir('{}/plotting/plots/{}/normed/'.format(os.getcwd(), output_tag))
            fig.savefig('{0}/plotting/plots/{1}/normed/{1}_{2}_normalised.pdf'.format(os.getcwd(), output_tag, var))
            plt.close()



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group('Required Arguments')
    required_args.add_argument('-c','--config', action='store', required=True)
    opt_args = parser.add_argument_group('Optional Arguements')
    opt_args.add_argument('-r','--reload_samples', action='store_true', default=False)
    opt_args.add_argument('-b','--n_bins',  default=34, type=int)
    opt_args.add_argument('-P','--pt_reweight',  action='store_true', default=False)
    options=parser.parse_args()
    main(options)
