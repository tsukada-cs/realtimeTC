#!/bin/bash
cd $HOME/git/realtimeTC
git pull
git -C $HOME/git/TCtools pull

# Functions
run_python_script() {
    $HOME/anaconda3/envs/tc/bin/python "$@"
}

# Activate conda environment
conda activate tc

# Sync
echo "---------------- Sync remote ----------------"
rsync -av tc-times@www1163.sakura.ne.jp:users/tsukada/private/data/ data/ 
rsync -av tc-times@www1163.sakura.ne.jp:www/index.html www/index.html

# b01 acquire bset track
echo "---------------- b01 ----------------"
basins="AL EP WP IO SH"
# basins="AL"
year=$(date +%Y)
run_python_script scripts/b01_update_btk.py -y $year -b $basins -p data/tclist.csv -o data/TCs

# current_month=$(date +%m)
# if [ $current_month -eq 01 ]; then
# lastyear=$((current_year - 1))
# run_python_script scripts/b01_update_btk.py -y $lastyear -b $=basins -p data/tclist.csv -o data/TCs
# fi

# b02 listup latest IDs
echo "---------------- b02 ----------------"
time_cutoff=2
run_python_script scripts/b02_listup_updated_IDs.py data/tclist.csv -o data/pickup_IDs.csv -y $year -b $basins --time_cutoff $time_cutoff

# b03 acquire SAR ATCF
echo "---------------- b03 ----------------"
run_python_script scripts/b03_acquire_NESDIS_SAR_ATCF.py

# b04 acquire JMA btk
echo "---------------- b04 ----------------"
run_python_script scripts/b04_acquire_pre_JMA_btk.py

# c01(p01) plot best track intensity
echo "---------------- c01 ----------------"
# run_python_script scripts/c01_call_p01.py --plot_NESDIS_SAR
run_python_script scripts/c01_call_p01.py --plot_NESDIS_SAR --plot_JMA

# h01 generate HTML
echo "---------------- h01 ----------------"
run_python_script scripts/h01_generate_html.py $HOME/git/realtimeTC/data/tclist.csv -i $HOME/git/realtimeTC/data/pickup_IDs.csv
rsync -a outputs/html/ www/html/


# sync data
rsync -a data/ tc-times@www1163.sakura.ne.jp:users/tsukada/private/data/
rsync -a --include='*.png' --exclude='*.csv' --exclude='*.txt' --prune-empty-dirs data/ www/data/

# Rsync www
echo "---------------- rsync www ----------------"
rsync -av www/ tc-times@www1163.sakura.ne.jp:www/