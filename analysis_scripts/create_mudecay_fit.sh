#! /usr/bin zsh

#Call the several scripts to create the muondecay fit

python muondecay.py $1 | grep micro > decays.tmp
python get_numbers.py decays.tmp > decays_to_fit.tmp
echo `cat decays_to_fit.tmp | wc -l` "muons decayed"
python fit_decays.py decays_to_fit.tmp

rm decays.tmp
rm decays_to_fit.tmp

eog fit.png




