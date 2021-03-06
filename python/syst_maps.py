#pass 6 names
syst_map  = {'jerUp'  : 
                      ['leadJetEn', 'leadJetMass', 'leadJetPt',
                       'subleadJetEn', 'subleadJetMass', 'subleadJetPt',
                       'subsubleadJetEn', 'subsubleadJetMass', 'subsubleadJetPt',
                       'dijetPt', 'dijetMass'],

             'jerDown': 
                      ['leadJetEn', 'leadJetMass', 'leadJetPt',
                       'subleadJetEn', 'subleadJetMass', 'subleadJetPt',
                       'subsubleadJetEn', 'subsubleadJetMass', 'subsubleadJetPt',
                       'dijetPt', 'dijetMass'],

             'jesTotalUp': 
                      ['leadJetEn', 'leadJetMass', 'leadJetPt',
                      'subleadJetEn', 'subleadJetMass', 'subleadJetPt',
                      'subsubleadJetEn', 'subsubleadJetMass', 'subsubleadJetPt',
                      'dijetPt', 'dijetMass'],

             'jesTotalDown': 
                      ['leadJetEn', 'leadJetMass', 'leadJetPt',
                       'subleadJetEn', 'subleadJetMass', 'subleadJetPt',
                       'subsubleadJetEn', 'subsubleadJetMass', 'subsubleadJetPt',
                       'dijetPt', 'dijetMass'],

             'ElPtScaleUp': 
                      ['leadElectronEn', 'leadElectronMass', 'leadElectronPt', 
                       #'subleadElectronEn', 'subleadElectronMass', 'subleadElectronPt', #never use these
                       #'subsubleadElectronEn', 'subsubleadElectronMass', 'subsubleadElectronPt', never use these
                       'leadElectronPtOvM', 'subleadElectronPtOvM', 'dielectronMass', 'dielectronPt'
                      ],

             'ElPtScaleDown': 
                      ['leadElectronEn', 'leadElectronMass', 'leadElectronPt', 
                       #'subleadElectronEn','subleadElectronMass', 'subleadElectronPt', #never use these
                       #'subsubleadElectronEn', 'subsubleadElectronMass', 'subsubleadElectronPt', #never use these
                       'leadElectronPtOvM', 'subleadElectronPtOvM', 'dielectronMass', 'dielectronPt'
                      ]
            }

#variables that effect only event weights e.g. pre-firing correction. Fill nominal tree for these
weight_systs = {'L1PreFiringWeight': ['Dn', 'Nom', 'Up']
               }
