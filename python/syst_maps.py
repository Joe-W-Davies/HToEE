
syst_map  = {#'jerUp'  : 
             #         ['leadJetEn','leadJetPt', 'leadJetEta', 'leadJetPhi', 'leadJetQGL', #'leadJetMass',
             #          'subleadJetEn', 'subleadJetPt','subleadJetEta', 'subleadJetPhi', 'subleadJetQGL', #'subleadJetMass', 
             #          'subsubleadJetEn', 'subsubleadJetPt','subsubleadJetEta', 'subsubleadJetPhi', 'subsubleadJetQGL', #'subsubleadJetMass',  #NOTE: can remove this line for ggH MVA
             #          'dijetMass', 'dijetAbsDEta', 'dijetDPhi', 'dijetMinDRJetEle', #'dijetPt', 
             #          'dijetCentrality', 'dijetDieleAbsDPhiTrunc','dijetDieleAbsDEta', 
             #          'subleadJetDieleDEta', 'subleadJetDieleDPhi' ##FIXME ignore as incorrect treatment in the dumper'leadJetDieleDPhi','leadJetDieleDEta', 
             #          ], 
             #'jerDown': 
             #         ['leadJetEn','leadJetPt', 'leadJetEta', 'leadJetPhi', 'leadJetQGL', #'leadJetMass',
             #          'subleadJetEn', 'subleadJetPt','subleadJetEta', 'subleadJetPhi', 'subleadJetQGL', #'subleadJetMass', 
             #          'subsubleadJetEn', 'subsubleadJetPt','subsubleadJetEta', 'subsubleadJetPhi', 'subsubleadJetQGL', #'subsubleadJetMass',  #NOTE: can remove this line for ggH MVA
             #          'dijetMass', 'dijetAbsDEta', 'dijetDPhi', 'dijetMinDRJetEle', #'dijetPt', 
             #          'dijetCentrality', 'dijetDieleAbsDPhiTrunc','dijetDieleAbsDEta', 
             #          'subleadJetDieleDEta', 'subleadJetDieleDPhi' ##FIXME ignore as incorrect treatment in the dumper'leadJetDieleDPhi','leadJetDieleDEta', 
             #          ], 
             #'jesTotalUp': 
             #         ['leadJetEn','leadJetPt', 'leadJetEta', 'leadJetPhi', 'leadJetQGL', #'leadJetMass',
             #          'subleadJetEn', 'subleadJetPt','subleadJetEta', 'subleadJetPhi', 'subleadJetQGL', #'subleadJetMass', 
             #          'subsubleadJetEn', 'subsubleadJetPt','subsubleadJetEta', 'subsubleadJetPhi', 'subsubleadJetQGL', #'subsubleadJetMass',  #NOTE: can remove this line for ggH MVA
             #          'dijetMass', 'dijetAbsDEta', 'dijetDPhi', 'dijetMinDRJetEle', #'dijetPt', 
             #          'dijetCentrality', 'dijetDieleAbsDPhiTrunc','dijetDieleAbsDEta', 
             #          'subleadJetDieleDEta', 'subleadJetDieleDPhi' ##FIXME ignore as incorrect treatment in the dumper'leadJetDieleDPhi','leadJetDieleDEta', 
             #          ], 
             #'jesTotalDown': 
             #         ['leadJetEn','leadJetPt', 'leadJetEta', 'leadJetPhi', 'leadJetQGL', #'leadJetMass',
             #          'subleadJetEn', 'subleadJetPt','subleadJetEta', 'subleadJetPhi', 'subleadJetQGL', #'subleadJetMass', 
             #          'subsubleadJetEn', 'subsubleadJetPt','subsubleadJetEta', 'subsubleadJetPhi', 'subsubleadJetQGL', #'subsubleadJetMass',  #NOTE: can remove this line for ggH MVA
             #          'dijetMass','dijetAbsDEta', 'dijetDPhi', 'dijetMinDRJetEle', #'dijetPt', 
             #          'dijetCentrality', 'dijetDieleAbsDPhiTrunc','dijetDieleAbsDEta', 
             #          'subleadJetDieleDEta', 'subleadJetDieleDPhi' ##FIXME ignore as incorrect treatment in the dumper'leadJetDieleDPhi','leadJetDieleDEta', 
             #         ],
             'ElPtScaleUp': 
                      ['leadElectronEta', 'leadElectronPt',#'leadElectronEn', 'leadElectronPt','leadElectronPhi', #'leadElectronMass', 
                       'subleadElectronEta', 'subleadElectronPt',#'subleadElectronPhi', #do we use phi?
                       #'subleadElectronEn', 'subleadElectronMass', 'subleadElectronPt', #never use these
                       #'subsubleadElectronEn', 'subsubleadElectronMass', 'subsubleadElectronPt', never use these
                       'leadElectronPtOvM', 'subleadElectronPtOvM', 'dielectronMass', 'dielectronPt',
                       'dielectronCosPhi', 'dijetMinDRJetEle', 'dijetCentrality', 'dijetDieleAbsDPhiTrunc',
                       'dijetDieleAbsDEta', 'leadJetDieleDPhi', 'leadJetDieleDEta', 'subleadJetDieleDPhi',
                       'subleadJetDieleDEta'
                      ],
             'ElPtScaleDown': 
                      ['leadElectronEta', 'leadElectronPt',#'leadElectronEn', 'leadElectronPt', 'leadElectronPhi', #'leadElectronMass', 
                       'subleadElectronEta', 'subleadElectronPt', #'subleadElectronPhi', #do we use phi?
                       #'subleadElectronEn', 'subleadElectronMass', 'subleadElectronPt', #never use these
                       #'subsubleadElectronEn', 'subsubleadElectronMass', 'subsubleadElectronPt', never use these
                       'leadElectronPtOvM', 'subleadElectronPtOvM', 'dielectronMass', 'dielectronPt',
                       'dielectronCosPhi', 'dijetMinDRJetEle', 'dijetCentrality', 'dijetDieleAbsDPhiTrunc',
                       'dijetDieleAbsDEta', 'leadJetDieleDPhi', 'leadJetDieleDEta', 'subleadJetDieleDPhi',
                       'subleadJetDieleDEta'
                      ],
            }

#variables that effect only event weights e.g. pre-firing correction. Fill nominal tree for these
#the nested dict values (list 1) are the down, nominal, and up string exts for the systematic in the key.
#the nested dict values (list 2) are the year this systematic effects
weight_systs = {#'L1PreFiringWeight': {'exts':['_Dn', '_Nom', '_Up'], 'years':['2016', '2017']},
                #'ElectronIDSF':      {'exts':['Down', '', 'Up'], 'years':['2016', '2017', '2018']},
                #'ElectronRecoSF':    {'exts':['Down', '', 'Up'], 'years':['2016', '2017', '2018']},
                #'TriggerSF':         {'exts':['Down', '', 'Up'], 'years':['2016', '2017', '2018']}
               }


