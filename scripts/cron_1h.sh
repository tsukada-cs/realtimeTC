conda activate tc

# sync
bash $HOME/git/realtimeTC/scripts/sync_remote.sh

# b01 acquire bset track
echo "---------------- b01 ----------------"
typeset -a basins=("AL" "EP" "WP" "IO" "SH")
year=$(date +%Y)
for basin in "${basins[@]}"; do
    $HOME/anaconda3/envs/tc/bin/python $HOME/git/realtimeTC/scripts/b01_update_btk.py -y $year -b $basin -p $HOME/git/realtimeTC/refdata/TCs/tclist.csv -o $HOME/git/realtimeTC/refdata/TCs/JTWC_pre_btk
done

current_month=$(date +%m)
if [ $current_month -eq 01 ]; then
    lastyear=$((current_year - 1))
    for basin in "${basins[@]}"; do
        $HOME/anaconda3/envs/tc/bin/python $HOME/git/realtimeTC/scripts/b01_update_btk.py -y $lastyear -b $basin -p $HOME/git/realtimeTC/refdata/TCs/tclist.csv -o $HOME/git/realtimeTC/refdata/TCs/JTWC_pre_btk
    done
fi

# b02 listup latest IDs
echo "---------------- b02 ----------------"
$HOME/anaconda3/envs/tc/bin/python $HOME/git/realtimeTC/scripts/b02_listup_updated_IDs.py $HOME/git/realtimeTC/refdata/TCs/tclist.csv -o $HOME/git/realtimeTC/refdata/TCs/latest_IDlist.csv

# b03 acquire SAR ATCF
echo "---------------- b03 ----------------"
$HOME/anaconda3/envs/tc/bin/python $HOME/git/realtimeTC/scripts/b03_acquire_NESDIS_SAR_ATCF.py

# c01(p01) plot best track intensity
echo "---------------- c01 ----------------"
$HOME/anaconda3/envs/tc/bin/python $HOME/git/realtimeTC/scripts/c01_call_p01.py --plot_NESDIS_SAR

# h01 generate html
echo "---------------- h01 ----------------"
$HOME/anaconda3/envs/tc/bin/python $HOME/git/realtimeTC/scripts/h01_generate_html.py

# rsync images
echo "---------------- rsync images ----------------"
rsync -av $HOME/git/realtimeTC/outputs/JTWC_pre_intensity/ tc-times@www1163.sakura.ne.jp:www/tmp/

# rsync tclist.csv
echo "---------------- rsync tclist.csv ----------------"
rsync -av $HOME/git/realtimeTC/refdata/TCs/tclist.csv tc-times@www1163.sakura.ne.jp:tsukada/share/