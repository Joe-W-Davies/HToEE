#!/bin/bash

cd /vols/cms/jwd18/Hee/MLCategorisation/CMSSW_10_2_0/src/HToEE
source setup.sh

declare -a systs=("jesTotalUp" "jesTotalDown" "jerUp" "jerDown" "ElPtScaleUp" "ElPtScaleDown")
#declare -a systs=("jesTotalUp")

##2016-A
##usual systs
#for syst in "${systs[@]}"
#do
#    python categoryOpt/generic_tagger.py -c configs/tag_seq_config_2016A.yaml -M configs/mva_boundaries_config.yaml -d -S "$syst"
#done
##weight systs (plus nominal branches)
python categoryOpt/generic_tagger.py -c configs/tag_seq_config_2016A.yaml -M configs/mva_boundaries_config.yaml -d -W -r
##data with no syst variations
#python categoryOpt/generic_tagger.py -c configs/tag_seq_config_2016A.yaml -M configs/mva_boundaries_config.yaml -d -D

##2016-B
##usual systs
#for syst in "${systs[@]}"
#do
#    python categoryOpt/generic_tagger.py -c configs/tag_seq_config_2016B.yaml -M configs/mva_boundaries_config.yaml -d -S "$syst"
#done
##weight systs (plus nominal branches)
#python categoryOpt/generic_tagger.py -c configs/tag_seq_config_2016B.yaml -M configs/mva_boundaries_config.yaml -d -W 
##data with no syst variations
#python categoryOpt/generic_tagger.py -c configs/tag_seq_config_2016B.yaml -M configs/mva_boundaries_config.yaml -d -D -r

##2017
##usual systs
#for syst in "${systs[@]}"
#do
#    python categoryOpt/generic_tagger.py -c configs/tag_seq_config_2017.yaml -M configs/mva_boundaries_config.yaml -d -S "$syst" -r
#done
##weight systs (plus nominal branches)
#python categoryOpt/generic_tagger.py -c configs/tag_seq_config_2017.yaml -M configs/mva_boundaries_config.yaml -d -W -r
##data with no syst variations
#python categoryOpt/generic_tagger.py -c configs/tag_seq_config_2017.yaml -M configs/mva_boundaries_config.yaml -d -D -r

##2018
##usual systs
#for syst in "${systs[@]}"
#do
#    python categoryOpt/generic_tagger.py -c configs/tag_seq_config_2018.yaml -M configs/mva_boundaries_config.yaml -d -S "$syst" -r
#done
##weight systs (plus nominal branches)
#python categoryOpt/generic_tagger.py -c configs/tag_seq_config_2018.yaml -M configs/mva_boundaries_config.yaml -d -W -r
##data with no syst variations
#python categoryOpt/generic_tagger.py -c configs/tag_seq_config_2018.yaml -M configs/mva_boundaries_config.yaml -d -D -r
