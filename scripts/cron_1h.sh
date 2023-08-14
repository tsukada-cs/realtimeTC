conda activate tc

typeset -a basins=("AL" "EP" "WP" "IO" "SH")
year=$(date +%Y)
for basin in "${basins[@]}"; do
    echo "=====" $year $basin "====="
    $HOME/anaconda3/envs/tc/bin/python $HOME/git/realtimeTC/scripts/b01_update_btk.py -y $year -b $basin -p $HOME/git/realtimeTC/refdata/TCs/tclist.csv -o $HOME/git/realtimeTC/refdata/TCs/JTWC_pre_btk
    rsync -av $HOME/git/realtimeTC/outputs/JTWC_pre_intensity/ tc-times@www1163.sakura.ne.jp:www/tmp/
done

current_month=$(date +%m)
if [ $current_month -eq 01 ]; then
    lastyear=$((current_year - 1))
    for basin in "${basins[@]}"; do
        $HOME/anaconda3/envs/tc/bin/python $HOME/git/realtimeTC/scripts/b01_update_btk.py -y $lastyear -b $basin -p $HOME/git/realtimeTC/refdata/TCs/tclist.csv -o $HOME/git/realtimeTC/refdata/TCs/JTWC_pre_btk
    done
fi

rsync -av $HOME/git/realtimeTC/refdata/TCs/tclist.csv tc-times@www1163.sakura.ne.jp:tsukada/share/
