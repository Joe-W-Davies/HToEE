import argparse
import numpy as np
import yaml
import pickle

from catOptim import CatOptim
from DataHandling import ROOTHelpers
from PlottingUtils import Plotter
from NeuralNets import LSTM_DNN

def main(options):

    #take options from the yaml config
    with open(options.config, 'r') as config_file:
        config            = yaml.load(config_file)
        output_tag        = config['output_tag']

        mc_dir            = config['mc_file_dir']
        mc_fnames         = config['mc_file_names']
  
        data_dir          = config['data_file_dir']
        data_fnames       = config['data_file_names']

        proc_to_tree_name = config['proc_to_tree_name']       

        train_vars        = config['train_vars']
        vars_to_add       = config['vars_to_add']
        presel            = config['preselection']

        #load the mc dataframe for all years
        root_obj = ROOTHelpers(output_tag, mc_dir, mc_fnames, data_dir, data_fnames, proc_to_tree_name, train_vars, vars_to_add, presel)

        for sig_obj in root_obj.sig_objects:
            root_obj.load_mc(sig_obj, reload_samples=options.reload_samples)
        if not options.data_as_bkg:
            for bkg_obj in root_obj.bkg_objects:
                root_obj.load_mc(bkg_obj, bkg=True, reload_samples=options.reload_samples)
        else:
            for data_obj in root_obj.data_objects:
                root_obj.load_data(data_obj, reload_samples=options.reload_samples)
        root_obj.concat()

        print 'loading classifier: {}'.format(options.model)
        clf = pickle.load(open("{}".format(options.model), "rb"))

        sig_weights   = root_obj.mc_df_sig['weight'].values
        sig_m_ee      = root_obj.mc_df_sig['dielectronMass'].values
        pred_prob_sig = clf.predict_proba(root_obj.mc_df_sig[train_vars].values)

        if options.data_as_bkg: 
            bkg_weights   = root_obj.data_df['weight'].values
            bkg_m_ee      = root_obj.data_df['dielectronMass'].values
            pred_prob_bkg = clf.predict_proba(root_obj.data_df[train_vars].values)

        else: 
            bkg_weights   = root_obj.mc_df_bkg['weight'].values
            bkg_m_ee      = root_obj.mc_df_bkg['dielectronMass'].values
            pred_prob_bkg = clf.predict_proba(root_obj.mc_df_bkg[train_vars].values)

        #set up optimiser ranges and no. categories to test if non-cut based
        ranges    = [ [0.1,1.], [0,1.] ]
        names     = ['{}_score'.format(output_tag), 'Third_class_score'] 
        #names     = ['{}_score'.format(output_tag), 'bkg_class'] 
        print_str = ''
        cats = [1]
        AMS  = []

        for n_cats in cats:
            optimiser = CatOptim(sig_weights, sig_m_ee, [pred_prob_sig[:,2],pred_prob_sig[:,1]], bkg_weights, bkg_m_ee, [pred_prob_bkg[:,2],pred_prob_bkg[:,1]], n_cats, ranges, names)
            #optimiser = CatOptim(sig_weights, sig_m_ee, [pred_prob_sig[:,2],pred_prob_sig[:,0]], bkg_weights, bkg_m_ee, [pred_prob_bkg[:,2],pred_prob_bkg[:,0]], n_cats, ranges, names)
            #optimiser.setOpposite('Third_class_score')
            #optimiser.setOpposite('bkg_class') #FIXME: trying this for bkg instead of EWKZ
            optimiser.optimise(1, options.n_iters) #set lumi to 1 as already scaled when loading in
            print_str += 'Results for {} categories : \n'.format(n_cats)
            print_str += optimiser.getPrintableResult()
            AMS.append(optimiser.bests.totSignif)
        print '\n {}'.format(print_str)


        #make nCat vs AMS plots
        Plotter.cats_vs_ams(cats, AMS, output_tag)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group('Required Arguments')
    required_args.add_argument('-c','--config', action='store', required=True)
    required_args.add_argument('-m','--model', action='store', required=True)
    opt_args = parser.add_argument_group('Optional Arguements')
    opt_args.add_argument('-r','--reload_samples', action='store_true', default=False)
    opt_args.add_argument('-i','--n_iters', action='store', default=5000, type=int)
    opt_args.add_argument('-d','--data_as_bkg', action='store_true', default=False)
    options=parser.parse_args()
    main(options)
