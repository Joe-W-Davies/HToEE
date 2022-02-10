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
        mH                = config['mH']

        mc_dir            = config['mc_file_dir']
        mc_fnames         = config['mc_file_names']
  
        data_dir          = config['data_file_dir']
        data_fnames       = config['data_file_names']

        proc_to_tree_name = config['proc_to_tree_name']       

        train_vars        = config['train_vars']
        vars_to_add       = config['vars_to_add']
        presel            = config['preselection']

        #load the mc dataframe for all years
        root_obj = ROOTHelpers(output_tag, mc_dir, mc_fnames, data_dir, data_fnames, proc_to_tree_name, train_vars, vars_to_add, presel, mH=mH)

        for sig_obj in root_obj.sig_objects:
            root_obj.load_mc(sig_obj, reload_samples=options.reload_samples)
        if not options.data_as_bkg:
            for bkg_obj in root_obj.bkg_objects:
                root_obj.load_mc(bkg_obj, bkg=True, reload_samples=options.reload_samples)
        else:
            for data_obj in root_obj.data_objects:
                root_obj.load_data(data_obj, reload_samples=options.reload_samples)
        root_obj.concat()


        ########################################################################
        #FOR GGH BDT: add residual VBF events that dont pass the VBF preselection
        #print 'before'
        #vbf_train_vars  = ['dijetAbsDEta', 'dijetDPhi','dijetMinDRJetEle', 'dijetMass', 
        #'dijetDieleAbsDPhiTrunc', 'dijetDieleAbsDEta', 'dijetCentrality',
        #'leadJetDieleDPhi', 'subleadJetDieleDPhi', 'leadJetDieleDEta', 'subleadJetDieleDEta',
        #'leadElectronPtOvM', 'subleadElectronPtOvM', 'dielectronPt',
        #'leadJetEn', 'leadJetPt', 'leadJetEta', 'leadJetPhi','leadJetQGL', 
        #'subleadJetEn', 'subleadJetPt', 'subleadJetEta', 'subleadJetPhi','subleadJetQGL',
        #'subsubleadJetEn', 'subsubleadJetPt', 'subsubleadJetEta', 'subsubleadJetPhi', 'subsubleadJetQGL'
        #] 
        #clf = pickle.load(open("models/VBF_BDT_clf.pickle.dat", "rb"))
        #root_obj.mc_df_sig['VBF_score'] = clf.predict_proba(root_obj.mc_df_sig[vbf_train_vars].values)[:,1:].ravel()
        #add_failed_vbf_events = "(dijetMass<250 or leadJetPt<40 or subleadJetPt<25 or VBF_score<0.497) and proc=='VBF'"
        #ggH_df = root_obj.mc_df_sig[root_obj.mc_df_sig.proc=="ggH"]
        #VBF_failed_df = root_obj.mc_df_sig.query(add_failed_vbf_events)
        #root_obj.mc_df_sig = None
        #import pandas as pd
        #root_obj.mc_df_sig = pd.concat([VBF_failed_df, ggH_df]) # we read all VBF events in, but only want the ones that dont enter VBF cats!
        #########################################################################


        print 'loading classifier: {}'.format(options.model)
        clf = pickle.load(open("{}".format(options.model), "rb"))

        sig_weights   = root_obj.mc_df_sig['weight'].values
        sig_m_ee      = root_obj.mc_df_sig['dielectronMass'].values
        pred_prob_sig = clf.predict_proba(root_obj.mc_df_sig[train_vars].values)[:,1:].ravel()

        if options.data_as_bkg: 
            bkg_weights   = root_obj.data_df['weight'].values
            bkg_m_ee      = root_obj.data_df['dielectronMass'].values
            pred_prob_bkg = clf.predict_proba(root_obj.data_df[train_vars].values)[:,1:].ravel()

        else: 
            bkg_weights   = root_obj.mc_df_bkg['weight'].values
            bkg_m_ee      = root_obj.mc_df_bkg['dielectronMass'].values
            pred_prob_bkg = clf.predict_proba(root_obj.mc_df_bkg[train_vars].values)[:,1:].ravel()

        #set up optimiser ranges and no. categories to test if non-cut based
        ranges    = [ [0.15,1.] ]
        names     = ['{} score'.format(output_tag)] #arbitrary
        print_str = ''
        cats = [1,2,3,4]
        AMS  = []

        for n_cats in cats:
            optimiser = CatOptim(sig_weights, sig_m_ee, [pred_prob_sig], bkg_weights, bkg_m_ee, [pred_prob_bkg], n_cats, ranges, names)
            optimiser.optimise(1, options.n_iters) #set lumi to 1 as already scaled when loading in
            print_str += 'Results for {} categories : \n'.format(n_cats)
            print_str += optimiser.getPrintableResult()
            AMS.append(optimiser.bests.totSignif)
        print '\n {}'.format(print_str)

        #print category composition for events with some bad code
        optimiser.boundaries = {'{} score'.format(output_tag): [0.213, 0.577, 0.741, 0.890]}
        cat_counter = 0
        for icat in reversed(range(cats[-1])):
             print '\n Category {}'.format(cat_counter)
             if not options.data_as_bkg:
                 for bkg in root_obj.bkg_procs:
                     if icat==(cats[-1]-1): proc_mask = (root_obj.mc_df_bkg.proc==bkg) & (pred_prob_bkg>optimiser.boundaries[names[0]][icat])
                     else: proc_mask = (root_obj.mc_df_bkg.proc==bkg) & (pred_prob_bkg>optimiser.boundaries[names[0]][icat]) & (pred_prob_bkg<optimiser.boundaries[names[0]][icat+1])
                     print 'Raw number of {} events: {}'.format(bkg, np.sum(bkg_weights[proc_mask]))
             else: 
                 if icat==(cats[-1]-1): proc_mask = (pred_prob_bkg>optimiser.boundaries[names[0]][icat])
                 else: proc_mask = (pred_prob_bkg>optimiser.boundaries[names[0]][icat]) & (pred_prob_bkg<optimiser.boundaries[names[0]][icat+1])
                     
                 print 'Raw number of Data events: {}'.format(np.sum(bkg_weights[proc_mask]))

             for sig in root_obj.sig_procs:
                 if icat==(cats[-1]-1): proc_mask = (root_obj.mc_df_sig.proc==sig) & (pred_prob_sig>optimiser.boundaries[names[0]][icat])
                 else: proc_mask = (root_obj.mc_df_sig.proc==sig) & (pred_prob_sig>optimiser.boundaries[names[0]][icat]) & (pred_prob_sig<optimiser.boundaries[names[0]][icat+1])
                 print 'Raw number of {} events: {}'.format(sig, np.sum(sig_weights[proc_mask]))

             cat_counter+=1

        #make nCat vs AMS plots
        Plotter.cats_vs_ams(cats, AMS, output_tag)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group('Required Arguments')
    required_args.add_argument('-c','--config', action='store', required=True)
    required_args.add_argument('-m','--model', action='store', required=True)
    opt_args = parser.add_argument_group('Optional Arguements')
    opt_args.add_argument('-r','--reload_samples', action='store_true', default=False)
    opt_args.add_argument('-i','--n_iters', action='store', default=4000, type=int)
    opt_args.add_argument('-d','--data_as_bkg', action='store_true', default=False)
    options=parser.parse_args()
    main(options)
