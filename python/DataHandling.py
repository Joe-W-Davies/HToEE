#data handling imports
import sys 
import uproot as upr 
import numpy as np
import pandas as pd
import os
from os import path, system
import yaml

import pickle
from pickle import load, dump

from variables import nominal_vars, gen_vars, gev_vars
from syst_maps import syst_map, weight_systs
from Utils import Utils


class SampleObject(object):
    '''
    Book-keeping class to store attributes of each sample. One object to be used per year, per sample -
    practically this means one per ROOT file

    :param proc_tag: physics process name for the sample being read in
    :type proc_tag: string
    :param year: year for the sample being read in 
    :type year: int
    :param file_name: name of the ROOT file being read in
    :type file_name: string
    :param tree_path: name of the TTree for the sample, contained in the ROOT TDirectory
    :type tree_path: string
    :param vars_to_read: variables to read in from TTree. Dependent on the year e.g. L1PreFire weights for 16, 17 only.
     Note that currently only weight varying systematics vars can vary across years. All other variables are read in for every year
     including systematics that affect dont affect event weights. If we ever need this, can implement in the same way as weight systs.
    :type vars_to_read: list
    ''' 

    def __init__(self, proc_tag, year, file_name, tree_path, vars_to_read):
        self.proc_tag     = proc_tag
        self.year         = year
        self.file_name    = file_name
        self.tree_name    = tree_path
        self.vars_to_read = vars_to_read

class ROOTHelpers(object):
    """
    Class produce dataframes from any number of signal, background, or data processes 
    for multiple years of data taking

    :param out_tag: output string to be added to saved objectsm e.g. plots, dataframes, models, etc.
    :type out_tag: string
    :param mc_dir: directory where root files for simulation are held. Files for all years should be in this directory
    :type mc_dir: string
    :param mc_fnames: file names for simulated signal and background samples. Each has its own process key. 
                      Each process key has its own year keys. See any example training config for more detail.
    :type mc_fnames: dict
    :param data_dir: directory where root files for data are held. Files for all years should be in this directory
    :type: data_dir: string
    :param data_fnames: file names for Data samples. The key for all samples should be 'Data'.
                        This key has its own year keys. See any example training config for more detail.
    :type data_fnames: dict
    :param proc_to_tree_name: tree name split by physics process. Useful if trees have a process dependent name.
                              Should have one string per physics process name (per key)
    :type proc_to_tree_name: dict
    :param train_vars: variables to be used when training a classifier.
    :type train_vars: list
    :param vars_to_add: variables that are not in the input ROOT files, but will be added during sample processing.
                        Should become redundant when all variables are eventually in input files.
    :type vars_to_add: list
    :param presel_str: selection to be applied to all samples.
    :type presel_str: string
    :param read_systs: option to read in variables resulting from systematic variations e.g. JEC, JER, ...
    :type read_systs: bool
    """

    def __init__(self, out_tag, mc_dir, mc_fnames, data_dir, data_fnames, proc_to_tree_name, train_vars, vars_to_add, presel_str='', read_systs=False, mH='125'):

        self.years              = set()
        #self.lumi_map           = {'2016':35.9, '2017':41.5, '2018':59.7}
        self.lumi_map           = {'2016A':19.52, '2016B':16.81,'2017':41.5, '2018':59.7}
        self.lumi_scale         = True

        #get mass dependent XS and BR from cfg. Note only signals change as a fn of mH
        with open('MetaData/XS_BR.yaml', 'r') as XSBR_config:
            XSBR        = yaml.load(XSBR_config)
            self.XS_map = XSBR['XS_map'][mH]

        #get mass dependent eff and acc from cfg. Note only signals change as fn of mH
        with open('MetaData/eff_acc.yaml', 'r') as effAcc_config:
            effAcc       = yaml.load(effAcc_config)
            self.eff_acc = effAcc['eff_acc'][mH]

        self.MH = mH

        self.out_tag            = out_tag
        self.mc_dir             = mc_dir #FIXME: remove '\' using if_ends_with()
        self.data_dir           = data_dir
        self.save_dfs           = True

        if vars_to_add is None: vars_to_add = {}
        self.vars_to_add        = vars_to_add
        data_vars = nominal_vars
        core_vars = nominal_vars[:] #return copy so data_vars isn't modified
        missing_vars = [x for x in train_vars if x not in (nominal_vars+list(vars_to_add.keys()))]
        if len(missing_vars)!=0: raise IOError('Missing variables: {}'.format(missing_vars))

        self.train_vars         = train_vars
        self.cut_string         = presel_str

        self.sig_procs          = []
        self.sig_objects        = []
        for proc, year_to_file in mc_fnames['sig'].items():
            if proc not in self.sig_procs: self.sig_procs.append(proc) 
            else: raise IOError('Multiple versions of same signal proc trying to be read')
            for year, file_name in year_to_file.iteritems():
                self.years.add(year)
                if read_systs: final_mc_vars = self.add_year_dep_systs(core_vars, year)
                else: final_mc_vars = core_vars
                self.sig_objects.append( SampleObject(proc, year, file_name, proc_to_tree_name[proc], vars_to_read=final_mc_vars) )
 
        self.bkg_procs          = []
        self.bkg_objects        = []
        for proc, year_to_file in mc_fnames['bkg'].items():
            if proc not in self.bkg_procs: self.bkg_procs.append(proc) 
            else: raise IOError('Multiple versions of same background proc trying to be read')
            for year, file_name in year_to_file.iteritems():
                if year not in self.years:  raise IOError('Incompatible sample years')
                self.years.add(year)
                if read_systs: final_mc_vars = self.add_year_dep_systs(core_vars, year)
                else: final_mc_vars = core_vars
                self.bkg_objects.append( SampleObject(proc, year, file_name, proc_to_tree_name[proc], vars_to_read=final_mc_vars) )

        self.data_objects       = []
        for proc, year_to_file in data_fnames.items():
            for year, file_name in year_to_file.iteritems():
                if year not in self.years:  raise IOError('Incompatible sample years')
                self.years.add(year)
                self.data_objects.append( SampleObject(proc, year, file_name, proc_to_tree_name[proc], vars_to_read=data_vars) )

        self.mc_df_sig          = []
        self.mc_df_bkg          = []
        self.data_df            = []

    def add_year_dep_systs(self, core_vars, year):
        """
        Add systematic variables to nominal vars. Weight systematics are dependent on the year being considered.

        Arguments
        ---------
        core_vars: list
            all variables being read in except for systematics
        year: str
            year for dataframe being read in
            
        Returns
        -------
        final_mc_vars: new list of variables with year dependent weight systs and other systs added
        """

        final_mc_vars = core_vars[:]
        for syst_type in syst_map.keys():
            final_mc_vars += [var_name+'_'+syst_type for var_name in syst_map[syst_type]]

        for weight_syst in weight_systs.keys():
            if year in weight_systs[weight_syst]['years']: final_mc_vars += [weight_syst+ext for ext in weight_systs[weight_syst]['exts']]

        return final_mc_vars

    def no_lumi_scale(self):
        """ 
        Toggle lumi scaling on/off. Useful when producing ROOT files for worksapces/fits.
        """

        self.lumi_scale=False

    def scale_sig_partial_2016(self):
        """ 
        Scale 2016 signal by fractional lumi. Only used when producing ROOT files for worksapces -> fits.
        Note that this only works when one year is read in
        """

        print list(self.years)
        if len(self.years)>1: raise IOError("Need to read one year in separately in the 2016 tagger!")
        else: year = list(self.years)[0]
        sf = self.lumi_map[year]/35.9
        print 'Scaling year {} by : {}'.format(year,self.lumi_map[year]/35.9)
        self.mc_df_sig['weight'] = self.mc_df_sig['weight'] * sf

    def correct_energy_scale_2016(self, year='2016A', sf=1.003):
        """
        Note: must have run the SF derivation for 2016 pre-VFP samples first
        """
        from ROOT import TLorentzVector

        def calc_dielectron_mass(row):
        #get position vector of negative e in rest frame of ee system
            e_1 = TLorentzVector()
            e_1.SetPtEtaPhiM(row['shiftedLeadElectronPt'], row['leadElectronEta'], row['leadElectronPhi'], row['leadElectronMass'])
            e_2 = TLorentzVector()
            e_2.SetPtEtaPhiM(row['shiftedSubleadElectronPt'], row['subleadElectronEta'], row['subleadElectronPhi'], row['subleadElectronMass'])
            return (e_1 + e_2).M()

        def calc_dielectron_pt(row):
        #get position vector of negative e in rest frame of ee system
            e_1 = TLorentzVector()
            e_1.SetPtEtaPhiM(row['shiftedLeadElectronPt'], row['leadElectronEta'], row['leadElectronPhi'], row['leadElectronMass'])
            e_2 = TLorentzVector()
            e_2.SetPtEtaPhiM(row['shiftedSubleadElectronPt'], row['subleadElectronEta'], row['subleadElectronPhi'], row['subleadElectronMass'])
            return (e_1 + e_2).Pt()

        if len(self.years)==1 and ('2016A' in self.years):
            self.data_df['shiftedLeadElectronPt']    = self.data_df['leadElectronPt']*sf
            self.data_df['shiftedSubleadElectronPt'] = self.data_df['subleadElectronPt']*sf
            self.data_df['dielectronMass']           = self.data_df.apply(calc_dielectron_mass, axis=1)
            self.data_df['dielectronPt']           = self.data_df.apply(calc_dielectron_pt, axis=1)
            

    def encode_year(self):
        """
        Create a binary flag for each year as a column
        """

        for yr in self.lumi_map.keys():
            self.mc_df_sig[yr] = self.mc_df_sig[self.mc_df_sig.year==yr].values
            self.mc_df_bkg[yr] = self.mc_df_bkg[self.mc_df_sig.year==yr].values
            self.data_df[yr]   = self.data_df[self.mc_df_sig.year==yr].values

    def encode_n_jets(self):
        """
        Add N jets as column in df
        """

        def add_n_jets(row):
            if row['leadJetPt'] < 0: return 0
            elif row['subleadJetPt'] < 0: return 1
            elif row['subsubleadJetPt'] < 0: return 2
            else: return 3

        self.mc_df_sig['n_jets'] = self.mc_df_sig.apply(add_n_jets, axis=1)
        self.mc_df_bkg['n_jets'] = self.mc_df_bkg.apply(add_n_jets, axis=1)
        #self.data_df['n_jets']   = self.data_df.apply(add_n_jets, axis=1)

    def add_LabEleDieleDTheta(self):
        """
        Add angle between (the e- in rest frame of ee system) and (direction of ee system in lab frame) as requested by ARC
        """

        import ROOT
        from ROOT import TLorentzVector

        def calc_dAngle(row):
            #get position vector of dielectron in lab frame in terms of 3 vector
            dielectron_lab_p4 = TLorentzVector()
            dielectron_lab_p4.SetPtEtaPhiM(row['dielectronPt'], row['dielectronEta'], row['dielectronPhi'], row['dielectronMass'])

            #get position vector of negative e in rest frame of ee system
            e_minus_lab_p4 = TLorentzVector()
            if row['leadElectronCharge'] < 0:
                e_minus_lab_p4.SetPtEtaPhiM(row['leadElectronPt'], row['leadElectronEta'], row['leadElectronPhi'], row['leadElectronMass'])
            else:
                e_minus_lab_p4.SetPtEtaPhiM(row['subleadElectronPt'], row['subleadElectronEta'], row['subleadElectronPhi'], row['subleadElectronMass'])
            dielectron_lab_p3_booster = dielectron_lab_p4.BoostVector()
            e_minus_lab_p4.Boost(-dielectron_lab_p3_booster) #NOTE: now its the e minus in the dielectron COM frame!
            
            #return the angle between the two vectors computed above
            return dielectron_lab_p4.Angle(e_minus_lab_p4.Vect())

        self.mc_df_sig['eMinusDielectronDThetaLab'] = self.mc_df_sig.apply(calc_dAngle, axis=1)
        self.mc_df_bkg['eMinusDielectronDThetaLab'] = self.mc_df_bkg.apply(calc_dAngle, axis=1)
        self.data_df['eMinusDielectronDThetaLab']   = self.data_df.apply(calc_dAngle, axis=1)

    def load_mc(self, sample_obj, bkg=False, reload_samples=False, read_QCD_arrays=False):
        """
        Try to load mc dataframe. If it doesn't exist, read in the root file.
        This should be used once per year, if reading in multiple years.

        Arguments
        ---------
        sample_obj: SampleObject
            an instance of the SampleObject class. Used to unpack attributes of the sample.
        bkg: bool
            indicates if the simulated sample being processed is background.
        reload_samples: bool
            force all samples to be read in from the input ROOT files, even if the dataframes already exist.
            Useful if changes to input files have been made.
        """

        try: 
            if reload_samples: raise IOError
            elif not bkg: self.mc_df_sig.append( self.load_df(self.mc_dir+'DataFrames/', sample_obj.proc_tag, sample_obj.year) ) #FIXME add sig,bkg,data flag in load_Df args here to only save/read M125 samples for signal. at it does sig and bkg
            else: self.mc_df_bkg.append( self.load_df(self.mc_dir+'DataFrames/', sample_obj.proc_tag, sample_obj.year) )
        except IOError: 
            if not bkg: self.mc_df_sig.append( self.root_to_df(self.mc_dir, 
                                                               sample_obj.proc_tag,
                                                               sample_obj.file_name,
                                                               sample_obj.tree_name,
                                                               'sig', sample_obj.year,
                                                               sample_obj.vars_to_read,
                                                               read_QCD_arrays=read_QCD_arrays
                                                              )
                                             )
            else: self.mc_df_bkg.append( self.root_to_df(self.mc_dir,
                                                         sample_obj.proc_tag,
                                                         sample_obj.file_name, 
                                                         sample_obj.tree_name,
                                                         'bkg', sample_obj.year,
                                                         sample_obj.vars_to_read,
                                                         read_QCD_arrays=read_QCD_arrays
                                                        )
                                       )

    def load_data(self, sample_obj, reload_samples=False):
        """
        Try to load Data dataframe. If it doesn't exist, read in the root file.
        This should be used once per year, if reading in multiple years.

        Arguments
        ---------
        sample_obj: SampleObject
            an instance of the SampleObject class. Used to unpack attributes of the sample.
        reload_samples: bool
            force all samples to be read in from the input ROOT files, even if the dataframes alreadt exist.
            Useful if changes to input files have been made.
        """

        try: 
            if reload_samples: raise IOError
            else: self.data_df.append( self.load_df(self.data_dir+'DataFrames/', 'Data', sample_obj.year) )
        except IOError: 
            self.data_df.append( self.root_to_df(self.data_dir, sample_obj.proc_tag, sample_obj.file_name, sample_obj.tree_name, 'Data', sample_obj.year, sample_obj.vars_to_read) )

    def load_df(self, df_dir, proc, year):
        """
        Load pandas dataframe, for a given process and year. Check all variables need for training are in columns.

        Arguments
        ---------
        df_dir: string
            directory where pandas dataframes for each process x year are kept. 
        proc: string
            physics process name for dataframe being read in
        year: string
            year for dataframe being read in
            
        Returns
        -------
        df: pandas dataframe that was read in.
        """

        if proc != 'Data': 
            df = pd.read_csv('{}{}_M{}_{}_df_{}.csv'.format(df_dir, proc, self.MH, self.out_tag, year))
            missing_vars = [x for x in self.train_vars if x not in list(df.columns)+list(self.vars_to_add.keys())]
            if len(missing_vars)!=0: raise IOError('Missing variables in dataframe: {}. Reload with option -r and try again'.format(missing_vars)) #will actually catch this error but still exits later on
            else: print('Sucessfully loaded DataFrame: {}{}_M{}_{}_df_{}.csv'.format(df_dir, proc, self.MH, self.out_tag, year))
        else: 
            df = pd.read_csv('{}{}_{}_df_{}.csv'.format(df_dir, proc, self.out_tag, year))
            missing_vars = [x for x in self.train_vars if x not in list(df.columns)+list(self.vars_to_add.keys())]
            if len(missing_vars)!=0: raise IOError('Missing variables in dataframe: {}. Reload with option -r and try again'.format(missing_vars)) #will actually catch this error but still exits later on
            print('Sucessfully loaded DataFrame: {}{}_{}_df_{}.csv'.format(df_dir, proc, self.out_tag, year))

        return df    

    def root_to_df(self, file_dir, proc_tag, file_name, tree_name, flag, year, vars_to_read, read_QCD_arrays=False):
        """
        Load a single root file for signal, background or data, for a given year. Apply any preselection.
        If reading in simulated samples, apply lumi scaling and read in gen-level variables too

        Arguments
        ---------
        file_dir: string
            directory that the ROOT file being read in is contained.
        proc_tag: string
            name of the physics process for the sample.
        file_name: string
            name of ROOT file being read in.
        tree_name: string
            name of TTree contrained within the ROOT file being read in.
        flag: string
            flag to indicate signal ('sig'), background ('bkg'), or Data ('Data')

        Returns
        -------
        df: pandas dataframe created from the input ROOT file
        """

        print('Reading {} file: {}, for year: {}'.format(proc_tag, file_dir+file_name, year))
        df_file = upr.open(file_dir+file_name)
        df_tree = df_file[tree_name]
        del df_file

        if flag == 'Data':
            #can cut on data here as dont need to run MC_norm
            if 'pt_weight' in vars_to_read: vars_to_read = vars_to_read.remove('pt_weight')
            df = df_tree.pandas.df(vars_to_read).query(self.cut_string)
        else:
            #cannot cut on sim now as need to run MC_norm and need sumGenW before selection!
            df = df_tree.pandas.df(vars_to_read+gen_vars)
            #NOTE: dont apply cuts yet as need to do MC norm!
            if read_QCD_arrays: #kinf of janky but arrays are Awkward and have no pandas compatibility
                df_qcd_cols = []
                qcd_indexes = [0,1,3,5,7,8]
                for i in qcd_indexes: #2nd and 6th elements can be ignored as unphysical variations. 4 is nominal (=1)
                    df_qcd_cols.append( pd.DataFrame([l[i] for l in df_tree.array("LHEScaleWeight")]) )
                df_qcd = pd.concat(df_qcd_cols, axis=1, ignore_index=True)
                original_df_cols = df.columns.tolist()
                df = pd.concat([df,df_qcd], axis=1, ignore_index=True)
                df.columns = original_df_cols + ['qcd_scale_variation_'+str(v) for v in qcd_indexes]

        if len(self.cut_string)>0:
            if flag != 'Data':
                df = self.MC_norm(df, proc_tag, year)
                df = df.query(self.cut_string)
        else:
            if flag != 'Data':
                df = self.MC_norm(df, proc_tag, year)

        df = df.sample(frac=1).reset_index(drop=True)
        df = df.dropna()
        df['proc'] = proc_tag
        df['year'] = year

        #FIXME: add missing third jet centrality. Can delete once in dumper
        #df['thirdJetZepp'] = np.abs( df['subsubleadJetEta'] - 0.5*(df['leadJetEta'] - df['subleadJetEta']) )
        #df['subsubleadJetCentrality'] = np.exp( -4*(df['thirdJetZepp']/np.abs(df['leadJetEta'] - df['subleadJetEta']))**2 )
        #df[df.subsubleadJetEta<-100]['subsubleadJetCentrality'] = -999

        #FIXME: add missing ele ID and Reco systs. Now included in samples (since pass11)
        #if flag!='Data':
        #    df['ElectronIDSF_weight_Nom']   = df['leadElectronIDSF'] * df['subleadElectronIDSF'] 
        #    df['ElectronIDSF_weight_Dn']    = df['leadElectronIDSFDown'] * df['subleadElectronIDSFDown']
        #    df['ElectronIDSF_weight_Up']    = df['leadElectronIDSFUp'] * df['subleadElectronIDSFUp']

        #    df['ElectronRecoSF_weight_Nom'] = df['leadElectronRecoSF'] * df['subleadElectronRecoSF'] 
        #    df['ElectronRecoSF_weight_Dn']  = df['leadElectronRecoSFDown'] * df['subleadElectronRecoSFDown']
        #    df['ElectronRecoSF_weight_Up']  = df['leadElectronRecoSFUp'] * df['subleadElectronRecoSFUp']

        print('Number of events in final dataframe: {}'.format(np.sum(df['weight'].values)))
        #save everything
        if self.save_dfs:
            Utils.check_dir(file_dir+'DataFrames/') 
            if flag!='Data': 
                df.to_csv('{}/{}_M{}_{}_df_{}.csv'.format(file_dir+'DataFrames', proc_tag, self.MH, self.out_tag, year))
                print('Saved dataframe: {}/{}_M{}_{}_df_{}.csv'.format(file_dir+'DataFrames', proc_tag, self.MH, self.out_tag, year))
            else: 
                df.to_csv('{}/{}_{}_df_{}.csv'.format(file_dir+'DataFrames', proc_tag, self.out_tag, year))
                print('Saved dataframe: {}/{}_{}_df_{}.csv'.format(file_dir+'DataFrames', proc_tag, self.out_tag, year))

        return df

    def MC_norm(self, df, proc_tag, year):
        """
        Apply normalisation to get expected number of events (perform before prelection)
        Note that "weight" column already has exp SFs applied i.e. weight = genWeight * centralObjWeight

        End up with a normalised weight: weight = (event_weight * xs * eff * acc)/sum(genWeights)

        Arguments 
        ---------
        :param df: pandas Dataframe
            dataframe for simulated signal or background with weights to be normalised
        :param proc_tag: string
            name of the physics process for the dataframe
        :param year: string
            year corresponding to the dataframe being read in

        Returns
        -------
        df: normalised dataframes
        """

        #Do scaling that used to happen in flashgg: XS * BR(for sig only) eff * acc
        sum_w_gen = np.sum(df['genWeight'].values)
        print ('scaling by {} by XS: {}'.format(proc_tag, self.XS_map[proc_tag]))
        df['weight'] *= (self.XS_map[proc_tag]) 

        if self.lumi_scale: #should not be doing this in the final Tag producer
            print ('scaling by {} by Lumi: {} * 1000 /pb'.format(proc_tag, self.lumi_map[year]))
            df['weight'] *= self.lumi_map[year]*1000 #lumi is added earlier but XS is in pb, so need * 1000

        print ('scaling by {} by eff*acc: {}'.format(proc_tag, self.eff_acc[year][proc_tag]))
        df['weight'] *= (self.eff_acc[year][proc_tag])
        df['weight'] /= sum_w_gen

        print ('sumW for proc {}: {}'.format(proc_tag, np.sum(df['weight'].values)))

        return df

    def apply_more_cuts(self, cut_string):
        """
        Apply some additional cuts, after nominal preselection (which was applied when file was read in)

        Arguments
        ---------
        cut_string: string
            set of cuts to be applied to all variables
        """

        self.mc_df_sig          = self.mc_df_sig.query(cut_string)
        self.mc_df_bkg          = self.mc_df_bkg.query(cut_string)
        self.data_df            = self.data_df.query(cut_string)

    def concat(self):
        """
        Concat sample types (sig, bkg, data) together, if more than one df in the associated sample type list.
        Years will also be automatically concatennated over. Could split this up into another function if desired
        but year info is only needed for lumi scaling.

        If the list is empty (not reading anything), leave it empty
        """

        if len(self.mc_df_sig) == 1: self.mc_df_sig = self.mc_df_sig[0]
        elif len(self.mc_df_sig) == 0: pass
        else: self.mc_df_sig = pd.concat(self.mc_df_sig)

        if len(self.mc_df_bkg) == 1: self.mc_df_bkg = self.mc_df_bkg[0] 
        elif len(self.mc_df_bkg) == 0: pass
        else: self.mc_df_bkg = pd.concat(self.mc_df_bkg)

        if len(self.data_df) == 1: self.data_df = self.data_df[0] 
        elif len(self.data_df) == 0 : pass
        else: self.data_df = pd.concat(self.data_df)

    def apply_pt_rew(self, bkg_proc, presel, norm=True):
        """
        Derive a reweighting for a single bkg process in a m(ee) control region around the Z-peak, in bins on pT(ee),
        to map bkg process to Data. SFs for each year are derived separately. Then apply to SR.

        Note that if norming, we must apply the flat k-factor in the SR *after* pt-reweighting, since the latter
        doesn't preserve the normalisation

        Arguments
        ---------
        bkg_proc: string
            name of the physics process we want to re-weight. Nominally this is for Drell-Yan.
        year: string
            year to be re-weighted (perform this separately for each year)
        presel: string
            preselection to apply to go from the CR -> SR
        norm: bool
            normalise the simulated background to data. Results in a shape-only correction
        """

        #derive SFs
        year_to_scale_factors = {}
        for year in self.years:

            #pt_bins = np.linspace(0,180,101)
            #try not const binning:
            pt_bins = np.concatenate((np.linspace(0,40,26),np.linspace(44,80,10),np.linspace(85,180,20)))
            bkg_df = self.mc_df_bkg.query('proc=="{}" and year=="{}" and dielectronMass>80 and dielectronMass<100'.format(bkg_proc,year)) #FIXME
            data_df = self.data_df.query('year=="{}" and dielectronMass>80 and dielectronMass<100'.format(year))       #FIXME
            #bkg_df = self.mc_df_bkg.query('proc=="{}" and year=="{}" and dielectronMass>90 and dielectronMass<100'.format(bkg_proc,year))
            #data_df = self.data_df.query('year=="{}" and dielectronMass>90 and dielectronMass<100'.format(year))       

            #FIXME: here only norming DY events to data which is mainly DY...
            if norm: bkg_df['weight'] *= (np.sum(data_df['weight'])/np.sum(bkg_df['weight']))

            bkg_pt_binned, _ = np.histogram(bkg_df['dielectronPt'], bins=pt_bins, weights=bkg_df['weight'])
            data_pt_binned, bin_edges = np.histogram(data_df['dielectronPt'], bins=pt_bins)
            year_to_scale_factors[year] = data_pt_binned/bkg_pt_binned

        with open('/vols/cms/jwd18/Hee/MLCategorisation/CMSSW_10_2_0/src/HToEE/studies/ARC/SFs_per_year/sfs.pickle', 'wb') as handle:
            pickle.dump(year_to_scale_factors, handle, protocol=pickle.HIGHEST_PROTOCOL)         

        #put samples into SR phase space. 
        self.apply_more_cuts(presel)

        #apply pt-reweighting inSR
        #self.mc_df_bkg['weight'] = self.mc_df_bkg.apply(self.pt_reweight_helper, axis=1, args=[bkg_proc, bin_edges, year_to_scale_factors])

        #do not get an inedxing error when we try do index = length + 1, since len SFs = len bin_edges -1
        scaled_bkg_dfs = []
        for year in self.years:
            df_year_i = self.mc_df_bkg.query('year=="{}"'.format(year))
            scale_factors = year_to_scale_factors[year]
            for i_bin in range(len(scale_factors)):
                temp_df = df_year_i[df_year_i.dielectronPt > bin_edges[i_bin]] 
                temp_df = temp_df[temp_df.dielectronPt < bin_edges[i_bin+1]] 
                temp_df['weight'] *= scale_factors[i_bin]
                scaled_bkg_dfs.append(temp_df)  
            outside_rng_df = df_year_i[df_year_i.dielectronPt > bin_edges[-1]]
            scaled_bkg_dfs.append(outside_rng_df)
        
        self.mc_df_bkg = pd.concat(scaled_bkg_dfs)
        del scaled_bkg_dfs

        #use numpy select to apply year dependent k-factor to events. Much quicker than using pandas apply! can probs do it the same way as above for clarity but whatev
        if norm:
            normed_year_dfs_bkg = []
            for year in self.years:
                    df_bkg_year_i = self.mc_df_bkg.query('year=="{}"'.format(year))
                    df_data_year_i = self.data_df.query('year=="{}"'.format(year))
                    norm_factor = np.sum(df_data_year_i['weight']) / np.sum(df_bkg_year_i['weight'])
                    df_bkg_year_i['weight'] *= norm_factor
                    normed_year_dfs_bkg.append(df_bkg_year_i)

            self.mc_df_bkg = pd.concat( normed_year_dfs_bkg )

        for year in self.years:
            self.save_modified_dfs(year)


    def pt_reweight_helper(self, row, bkg_proc, bin_edges, scale_factors):
        """
        Function called in pandas apply() function, looping over rows and testing conditions. Can be called for
        single or double differential re-weighting.

        Tests which pT a bkg proc is, and if it is the proc to reweight, before
        applying a pT dependent scale factor to apply (derived from CR)
        
        If dielectron pT is above the max pT bin, just return the nominal weight (very small num of events)

        Arguments
        ---------
        row: pandas Series
            a single row of the dataframe being looped through. Automatically generated as first argument
            when using pandas apply()
        bkg_proc: string
            name of the physics process we want to re-weight. Nominally this is for Drell-Yan.
        bin_edges: numpy array
            edges of each pT bin, in which the re-weighting is applied
        scale_factors: numpy array
            scale factors to be applied in each pT bin

        Returns
        -------
        row['weight'] * scale-factor : float of the (modified) MC weight for a single event/dataframe row
        """

        if row['proc']==bkg_proc and row['dielectronPt']<bin_edges[-1]:
            rew_factors = scale_factors[row['year']]
            for i_bin in range(len(bin_edges)):
                if (row['dielectronPt'] > bin_edges[i_bin]) and (row['dielectronPt'] < bin_edges[i_bin+1]):
                    return row['weight'] * rew_factors[i_bin] 
        else:
            return row['weight'] 


    def pt_njet_reweight(self, bkg_proc, year, presel, norm_first=True):
        """
        Derive a reweighting for a single bkg process in a m(ee) control region around the Z-peak, double differentially 
        in bins on pT(ee) and nJets, to map bkg process to Data. Then apply this in the signal region.

        Arguments
        ---------
        bkg_proc: string
            name of the physics process we want to re-weight. Nominally this is for Drell-Yan.
        year: string
            year to be re-weighted (perform this separately for each year)
        presel: string
            preselection to apply to go from the CR -> SR
        norm_first: bool
            normalise the simulated background to data. Results in a shape-only correction
        """
        #FIXME: function is out of date with rest of code

        #can remove this once nJets is put in ntuples from dumper
        outcomes_mc_bkg = [ self.mc_df_bkg['leadJetPt'].lt(0),
                            self.mc_df_bkg['leadJetPt'].gt(0) & self.mc_df_bkg['subleadJetPt'].lt(0), 
                            self.mc_df_bkg['leadJetPt'].gt(0) & self.mc_df_bkg['subleadJetPt'].gt(0)
                          ]

        outcomes_data   = [ self.data_df['leadJetPt'].lt(0),
                            self.data_df['leadJetPt'].gt(0) & self.data_df['subleadJetPt'].lt(0), 
                            self.data_df['leadJetPt'].gt(0) & self.data_df['subleadJetPt'].gt(0)
                          ]
        jets    = [0, 1, 2] # 2 really means nJet >= 2

        self.mc_df_bkg['nJets'] = np.select(outcomes_mc_bkg, jets) 
        self.data_df['nJets'] = np.select(outcomes_data, jets) 

        #apply re-weighting
        pt_bins = np.linspace(0,200,101)
        jet_bins = [0,1,2]
        n_jets_to_sfs_map = {}


        #derive pt and njet based SFs
        for n_jets in jet_bins:
            if not n_jets==jet_bins[-1]: 
                bkg_df = self.mc_df_bkg.query('proc=="{}" and year=="{}" and dielectronMass>80 and dielectronMass<100 and nJets=={}'.format(bkg_proc,year, n_jets))
                data_df = self.data_df.query('year=="{}" and dielectronMass>80 and dielectronMass<100 and nJets=={}'.format(year,n_jets))       
            else: 
                bkg_df = self.mc_df_bkg.query('proc=="{}" and year=="{}" and dielectronMass>80 and dielectronMass<100 and nJets>={}'.format(bkg_proc,year, n_jets))
                data_df = self.data_df.query('year=="{}" and dielectronMass>80 and dielectronMass<100 and nJets>={}'.format(year,n_jets))       

            if norm_first:
                CR_norm_i_jet_bin = (np.sum(data_df['weight'])/np.sum(bkg_df['weight']))
                bkg_df['weight'] *= CR_norm_i_jet_bin

            bkg_pt_binned, _ = np.histogram(bkg_df['dielectronPt'], bins=pt_bins, weights=bkg_df['weight'])
            data_pt_binned, bin_edges = np.histogram(data_df['dielectronPt'], bins=pt_bins)
            n_jets_to_sfs_map[n_jets] = data_pt_binned/bkg_pt_binned

        #now apply the proc targeting selection on all dfs, and re-save. Then apply derived SFs
        self.apply_more_cuts(presel)
        if norm_first:
            SR_i_jet_to_norm = {}
            for n_jets in jet_bins:
                SR_i_jet_to_norm[n_jets] = np.sum(self.data_df['weight']) / np.sum(self.mc_df_bkg['weight'])
            self.mc_df_bkg['weight'] = self.mc_df_bkg.apply(self.pt_njet_reweight_helper, axis=1, args=[bkg_proc, year, bin_edges, n_jets_to_sfs_map, True, SR_i_jet_to_norm])

        else: self.mc_df_bkg['weight'] = self.mc_df_bkg.apply(self.pt_njet_reweight_helper, axis=1, args=[bkg_proc, year, bin_edges, n_jets_to_sfs_map, True, None])
        self.save_modified_dfs(year)
         
    def save_modified_dfs(self, year, ignore_sig=False, ignore_bkg=False, ignore_data=False):
        """
        Save dataframes again. Useful if modifications were made since reading in and saving e.g. pT reweighting or applying more selection
        (or both).

        Arguments
        ---------
        year: string
            year for which all samples being saved correspond to
        """

        print ('saving modified dataframes...')
        if not ignore_sig:
            for sig_proc in self.sig_procs:
                sig_df = self.mc_df_sig[np.logical_and(self.mc_df_sig.proc==sig_proc, self.mc_df_sig.year==year)]
                sig_df.to_csv('{}/{}_M{}_{}_df_{}.csv'.format(self.mc_dir+'DataFrames', sig_proc, self.MH, self.out_tag, year))
                print('saved dataframe: {}/{}_M{}_{}_df_{}.csv'.format(self.mc_dir+'DataFrames', sig_proc, self.MH, self.out_tag, year))

        if not ignore_bkg:
            for bkg_proc in self.bkg_procs:
                bkg_df = self.mc_df_bkg[np.logical_and(self.mc_df_bkg.proc==bkg_proc,self.mc_df_bkg.year==year)]
                bkg_df.to_csv('{}/{}_M{}_{}_df_{}.csv'.format(self.mc_dir+'DataFrames', bkg_proc, self.MH, self.out_tag, year)) #FIXME no need for MH here but will need to change it in original saver too!
                print('saved dataframe: {}/{}_M{}_{}_df_{}.csv'.format(self.mc_dir+'DataFrames', bkg_proc, self.MH, self.out_tag, year)) #FIXME no need for MH here but will need to change it in original saver too!

        if not ignore_data:
            data_df = self.data_df[self.data_df.year==str(year)]
            data_df.to_csv('{}/{}_{}_df_{}.csv'.format(self.data_dir+'DataFrames', 'Data', self.out_tag, year))
            print('saved dataframe: {}/{}_{}_df_{}.csv'.format(self.data_dir+'DataFrames', 'Data', self.out_tag, year))

