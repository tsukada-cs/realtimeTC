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
bash scripts/sync_remote.sh

# b01 acquire bset track
echo "---------------- b01 ----------------"
basins="AL EP WP IO SH"
# basins="WP"
year=$(date +%Y)
run_python_script scripts/b01_update_btk.py -y $year -b $basins -p refdata/TCs/tclist.csv -o refdata/TCs/JTWC_pre_btk

# current_month=$(date +%m)
# if [ $current_month -eq 01 ]; then
# lastyear=$((current_year - 1))
# run_python_script scripts/b01_update_btk.py -y $lastyear -b $basins -p refdata/TCs/tclist.csv -o refdata/TCs/JTWC_pre_btk
# fi

# b02 listup latest IDs
echo "---------------- b02 ----------------"
time_cutoff=48
run_python_script scripts/b02_listup_updated_IDs.py refdata/TCs/tclist.csv -o refdata/TCs/latest_IDlist.csv -y $year -b $basins --time_cutoff $time_cutoff

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
run_python_script scripts/h01_generate_html.py

# Rsync html
rsync -av outputs/html/file_list.html tc-times@www1163.sakura.ne.jp:www/

# Rsync images
echo "---------------- rsync images ----------------"
rsync -av outputs/JTWC_pre_intensity/ tc-times@www1163.sakura.ne.jp:www/tmp/


# Rsync tclist.csv
echo "---------------- rsync tclist.csv ----------------"
rsync -av refdata/TCs/tclist.csv tc-times@www1163.sakura.ne.jp:tsukada/share/