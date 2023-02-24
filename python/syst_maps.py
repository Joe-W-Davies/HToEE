
syst_map  = {'jerUp'  : 
                      ['leadJetEn','leadJetPt', 'leadJetEta', 'leadJetPhi', 'leadJetQGL', #'leadJetMass',
                       'subleadJetEn', 'subleadJetPt','subleadJetEta', 'subleadJetPhi', 'subleadJetQGL', #'subleadJetMass', 
                       'subsubleadJetEn', 'subsubleadJetPt','subsubleadJetEta', 'subsubleadJetPhi', 'subsubleadJetQGL', #'subsubleadJetMass',  #NOTE: can remove this line for ggH MVA
                       'dijetMass', 'dijetAbsDEta', 'dijetDPhi', 'dijetMinDRJetEle', #'dijetPt', 
                       'dijetCentrality', 'dijetDieleAbsDPhiTrunc','dijetDieleAbsDEta', 
                       'subleadJetDieleDEta', 'subleadJetDieleDPhi'
                      ],
             'jerDown': 
                      ['leadJetEn','leadJetPt', 'leadJetEta', 'leadJetPhi', 'leadJetQGL', #'leadJetMass',
                       'subleadJetEn', 'subleadJetPt','subleadJetEta', 'subleadJetPhi', 'subleadJetQGL', #'subleadJetMass', 
                       'subsubleadJetEn', 'subsubleadJetPt','subsubleadJetEta', 'subsubleadJetPhi', 'subsubleadJetQGL', #'subsubleadJetMass',  #NOTE: can remove this line for ggH MVA
                       'dijetMass', 'dijetAbsDEta', 'dijetDPhi', 'dijetMinDRJetEle', #'dijetPt', 
                       'dijetCentrality', 'dijetDieleAbsDPhiTrunc','dijetDieleAbsDEta', 
                       'subleadJetDieleDEta', 'subleadJetDieleDPhi'
                      ],
             'jesTotalUp': 
                      ['leadJetEn','leadJetPt', 'leadJetEta', 'leadJetPhi', 'leadJetQGL', #'leadJetMass',
                       'subleadJetEn', 'subleadJetPt','subleadJetEta', 'subleadJetPhi', 'subleadJetQGL', #'subleadJetMass', 
                       'subsubleadJetEn', 'subsubleadJetPt','subsubleadJetEta', 'subsubleadJetPhi', 'subsubleadJetQGL', #'subsubleadJetMass',  #NOTE: can remove this line for ggH MVA
                       'dijetMass', 'dijetAbsDEta', 'dijetDPhi', 'dijetMinDRJetEle', #'dijetPt', 
                       'dijetCentrality', 'dijetDieleAbsDPhiTrunc','dijetDieleAbsDEta', 
                       'subleadJetDieleDEta', 'subleadJetDieleDPhi'
                      ],
             'jesTotalDown': 
                      ['leadJetEn','leadJetPt', 'leadJetEta', 'leadJetPhi', 'leadJetQGL', #'leadJetMass',
                       'subleadJetEn', 'subleadJetPt','subleadJetEta', 'subleadJetPhi', 'subleadJetQGL', #'subleadJetMass', 
                       'subsubleadJetEn', 'subsubleadJetPt','subsubleadJetEta', 'subsubleadJetPhi', 'subsubleadJetQGL', #'subsubleadJetMass',  #NOTE: can remove this line for ggH MVA
                       'dijetMass', 'dijetAbsDEta', 'dijetDPhi', 'dijetMinDRJetEle', #'dijetPt', 
                       'dijetCentrality', 'dijetDieleAbsDPhiTrunc','dijetDieleAbsDEta', 
                       'subleadJetDieleDEta', 'subleadJetDieleDPhi'
                      ],
             'EELowR9ElPtScaleUp': 
                      ['dielectronMass', 
                       'leadElectronEta', 'leadElectronPt','subleadElectronPt',#'leadElectronEn', 'leadElectronPt','leadElectronPhi', #'leadElectronMass', 
                       #'subleadElectronEta', 'subleadElectronPt',#'subleadElectronPhi', #do we use phi?
                       #'subleadElectronEn', 'subleadElectronMass', 'subleadElectronPt', #never use these
                       #'subsubleadElectronEn', 'subsubleadElectronMass', 'subsubleadElectronPt', #never use these
                       'leadElectronPtOvM', 'subleadElectronPtOvM', 'dielectronPt',
                       'dielectronCosPhi',
                      ],
             'EELowR9ElPtScaleDown': 
                      ['dielectronMass', 
                       'leadElectronEta', 'leadElectronPt','subleadElectronPt',#'leadElectronEn', 'leadElectronPt','leadElectronPhi', #'leadElectronMass', 
                       #'subleadElectronEta', 'subleadElectronPt',#'subleadElectronPhi', #do we use phi?
                       #'subleadElectronEn', 'subleadElectronMass', 'subleadElectronPt', #never use these
                       #'subsubleadElectronEn', 'subsubleadElectronMass', 'subsubleadElectronPt', #never use these
                       'leadElectronPtOvM', 'subleadElectronPtOvM', 'dielectronPt',
                       'dielectronCosPhi',
                      ],
             'EEHighR9ElPtScaleUp': 
                      ['dielectronMass', 
                       'leadElectronEta', 'leadElectronPt','subleadElectronPt',#'leadElectronEn', 'leadElectronPt','leadElectronPhi', #'leadElectronMass', 
                       #'subleadElectronEta', 'subleadElectronPt',#'subleadElectronPhi', #do we use phi?
                       #'subleadElectronEn', 'subleadElectronMass', 'subleadElectronPt', #never use these
                       #'subsubleadElectronEn', 'subsubleadElectronMass', 'subsubleadElectronPt', #never use these
                       'leadElectronPtOvM', 'subleadElectronPtOvM', 'dielectronPt',
                       'dielectronCosPhi',
                      ],
             'EEHighR9ElPtScaleDown': 
                      ['dielectronMass', 
                       'leadElectronEta', 'leadElectronPt','subleadElectronPt',#'leadElectronEn', 'leadElectronPt','leadElectronPhi', #'leadElectronMass', 
                       #'subleadElectronEta', 'subleadElectronPt',#'subleadElectronPhi', #do we use phi?
                       #'subleadElectronEn', 'subleadElectronMass', 'subleadElectronPt', #never use these
                       #'subsubleadElectronEn', 'subsubleadElectronMass', 'subsubleadElectronPt', #never use these
                       'leadElectronPtOvM', 'subleadElectronPtOvM', 'dielectronPt',
                       'dielectronCosPhi',
                      ],
             'EBLowR9ElPtScaleUp': 
                      ['dielectronMass', 
                       'leadElectronEta', 'leadElectronPt','subleadElectronPt',#'leadElectronEn', 'leadElectronPt','leadElectronPhi', #'leadElectronMass', 
                       #'subleadElectronEta', 'subleadElectronPt',#'subleadElectronPhi', #do we use phi?
                       #'subleadElectronEn', 'subleadElectronMass', 'subleadElectronPt', #never use these
                       #'subsubleadElectronEn', 'subsubleadElectronMass', 'subsubleadElectronPt', #never use these
                       'leadElectronPtOvM', 'subleadElectronPtOvM', 'dielectronPt',
                       'dielectronCosPhi',
                      ],
             'EBLowR9ElPtScaleDown': 
                      ['dielectronMass', 
                       'leadElectronEta', 'leadElectronPt','subleadElectronPt',#'leadElectronEn', 'leadElectronPt','leadElectronPhi', #'leadElectronMass', 
                       #'subleadElectronEta', 'subleadElectronPt',#'subleadElectronPhi', #do we use phi?
                       #'subleadElectronEn', 'subleadElectronMass', 'subleadElectronPt', #never use these
                       #'subsubleadElectronEn', 'subsubleadElectronMass', 'subsubleadElectronPt', #never use these
                       'leadElectronPtOvM', 'subleadElectronPtOvM', 'dielectronPt',
                       'dielectronCosPhi',
                      ],
             'EBHighR9ElPtScaleUp': 
                      ['dielectronMass', 
                       'leadElectronEta', 'leadElectronPt','subleadElectronPt',#'leadElectronEn', 'leadElectronPt','leadElectronPhi', #'leadElectronMass', 
                       #'subleadElectronEta', 'subleadElectronPt',#'subleadElectronPhi', #do we use phi?
                       #'subleadElectronEn', 'subleadElectronMass', 'subleadElectronPt', #never use these
                       #'subsubleadElectronEn', 'subsubleadElectronMass', 'subsubleadElectronPt', #never use these
                       'leadElectronPtOvM', 'subleadElectronPtOvM', 'dielectronPt',
                       'dielectronCosPhi',
                      ],
             'EBHighR9ElPtScaleDown': 
                      ['dielectronMass', 
                       'leadElectronEta', 'leadElectronPt','subleadElectronPt',#'leadElectronEn', 'leadElectronPt','leadElectronPhi', #'leadElectronMass', 
                       #'subleadElectronEta', 'subleadElectronPt',#'subleadElectronPhi', #do we use phi?
                       #'subleadElectronEn', 'subleadElectronMass', 'subleadElectronPt', #never use these
                       #'subsubleadElectronEn', 'subsubleadElectronMass', 'subsubleadElectronPt', #never use these
                       'leadElectronPtOvM', 'subleadElectronPtOvM', 'dielectronPt',
                       'dielectronCosPhi',
                      ],

             'NonLinearityUp': 
                      ['dielectronMass', 
                       'leadElectronEta', 'leadElectronPt','subleadElectronPt',#'leadElectronEn', 'leadElectronPt','leadElectronPhi', #'leadElectronMass', 
                       #'subleadElectronEta', 'subleadElectronPt',#'subleadElectronPhi', #do we use phi?
                       #'subleadElectronEn', 'subleadElectronMass', 'subleadElectronPt', #never use these
                       'leadElectronPtOvM', 'subleadElectronPtOvM', 'dielectronPt',
                       'dielectronCosPhi', 'dijetMinDRJetEle', 'dijetCentrality', 'dijetDieleAbsDPhiTrunc',
                       'dijetDieleAbsDEta', 'leadJetDieleDPhi', 'leadJetDieleDEta', 'subleadJetDieleDPhi',
                       'subleadJetDieleDEta',
                       #'dielectronMass', 'leadElectronPtOvM', 'subleadElectronPtOvM', 'leadElectronPt', 'subleadElectronPt' #just include these is making mass plots (for memory)
                      ],
             'NonLinearityDown': 
                      ['dielectronMass', 
                       'leadElectronEta', 'leadElectronPt','subleadElectronPt',#'leadElectronEn', 'leadElectronPt','leadElectronPhi', #'leadElectronMass', 
                       #'subleadElectronEta', 'subleadElectronPt',#'subleadElectronPhi', #do we use phi?
                       #'subleadElectronEn', 'subleadElectronMass', 'subleadElectronPt', #never use these
                       'leadElectronPtOvM', 'subleadElectronPtOvM', 'dielectronPt',
                       'dielectronCosPhi', 'dijetMinDRJetEle', 'dijetCentrality', 'dijetDieleAbsDPhiTrunc',
                       'dijetDieleAbsDEta', 'leadJetDieleDPhi', 'leadJetDieleDEta', 'subleadJetDieleDPhi',
                       'subleadJetDieleDEta',
                       #'dielectronMass', 'leadElectronPtOvM', 'subleadElectronPtOvM', 'leadElectronPt', 'subleadElectronPt' #just include these is making mass plots (for memory)
                      ],
            }

#variables that effect only event weights e.g. pre-firing correction. Fill nominal tree for these
#the nested dict values (list 1) are the down, nominal, and up string exts for the systematic in the key.
#the nested dict values (list 2) are the year this systematic effects
#note this NEEDS to have the forma [down type, nominal, up type] else the syst treatment is wrong
weight_systs = {'L1PreFiringWeight': {'exts':['_Dn', '_Nom', '_Up'], 'years':['2016A','2016B', '2017']},
                'ElectronIDSF':      {'exts':['Down', '', 'Up'], 'years':['2016A', '2016B','2017', '2018']}, 
                'ElectronRecoSF':    {'exts':['Down', '', 'Up'], 'years':['2016A','2016B', '2017', '2018']},
                'TriggerSF':         {'exts':['Down', '', 'Up'], 'years':['2016A','2016B', '2017', '2018']}
               }


