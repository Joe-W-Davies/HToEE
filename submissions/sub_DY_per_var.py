import os, sys
import yaml
import argparse

def main(options):

    #take options from the yaml config
    with open(options.config, 'r') as config_file:
        config            = yaml.load(config_file)
        output_tag        = config['output_tag']
        train_vars        = config['train_vars']

        #for var in train_vars+['{}_mva'.format(options.proc)]:
        #for var in ['dielectronPt']:
        #for var in ['ggH_mva']:
        #for var in ['leadElectronPt','subleadElectronPt','dielectronMass']:
        for var in ['dielectronMass']:
        #for var in ['leadJetEta']:
        #for var in ['VBF_mva']:

             os.system('mkdir -p {}/submissions/{}_DYJobs'.format(os.getcwd(),output_tag))
             sub_file_name = '{}/submissions/{}_DYJobs/sub_DY_{}.sh'.format(os.getcwd(),output_tag,var)
             #sub_file_name = '{}/submissions/{}_DYJobs/sub_DY_{}.sh'.format(os.getcwd(),output_tag,var)
             #sub_command =  'python plotting/DY_validation.py -c configs/dy_valid_config_{}.yaml -M configs/mva_boundaries_config.yaml -s jesTotal ElPtScale jer -v {}'.format(options.proc.lower(),var)
             #sub_command =  'python plotting/DY_validation.py -c configs/dy_valid_config_{}.yaml -M configs/mva_boundaries_config.yaml -s jesTotal ElPtScale ElectronIDSF ElectronRecoSF TriggerSF -v {}'.format(options.proc.lower(),var)
             #for electron vars only
             sub_command =  'python plotting/DY_validation.py -c configs/dy_valid_config_{}.yaml -M configs/mva_boundaries_config.yaml -s EELowR9ElPtScale EBLowR9ElPtScale EEHighR9ElPtScale EBHighR9ElPtScale NonLinearity ElectronIDSF TriggerSF -v {} -r'.format(options.proc.lower(),var)
             #for electron+jet vars and output score
             #sub_command =  'python plotting/DY_validation.py -c configs/dy_valid_config_{}.yaml -M configs/mva_boundaries_config.yaml -s jesTotal jer ElPtScale ElectronIDSF TriggerSF -v {} -r'.format(options.proc.lower(),var)

             #sub_command =  'python plotting/DY_validation.py -c configs/dy_valid_config_{}.yaml -M configs/mva_boundaries_config.yaml -s jesTotal jer TriggerSF -v {} -r'.format(options.proc.lower(),var)
             #sub_command =  'python plotting/DY_validation.py -c configs/dy_valid_config_{}.yaml -M configs/mva_boundaries_config.yaml -s EELowR9ElPtScale EBLowR9ElPtScale EEHighR9ElPtScale EBHighR9ElPtScale jesTotal NonLinearity TriggerSF -v {} -r'.format(options.proc.lower(),var)

             with open('./submissions/sub_DY_single_vars.sh') as f_template:
                 with open(sub_file_name,'w') as f_sub:
                     for line in f_template.readlines():                 
                         if '!CWD!' in line: line = line.replace('!CWD!', os.getcwd())
                         if '!CMD!' in line: line = line.replace('!CMD!', '"{}"'.format(sub_command))
                         f_sub.write(line)                               
             os.system( 'qsub -o {} -e {} -q hep.q -l h_rt=3:0:0 -l h_vmem=24G -pe hep.pe 8 {}'.format(sub_file_name.replace('.sh','.log'), sub_file_name.replace('.sh','.err'), sub_file_name ) )
             #os.system( 'qsub -o {} -e {} -q hep.q -l h_rt=6:0:0 -pe hep.pe 8 {}'.format(sub_file_name.replace('.sh','.log'), sub_file_name.replace('.sh','.err'), sub_file_name ) )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group('Required Arguments')
    required_args.add_argument('-c','--config', action='store', required=True)
    required_args.add_argument('-p','--proc', action='store', required=True)
    options=parser.parse_args()
    main(options)
