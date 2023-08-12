# typeset -a basins=("AL" "EP" "WP")
typeset -a basins=("WP")

year=$(date +%Y)
for basin in "${basins[@]}"; do
    python /Users/tsukada/git/realtimeTC/scripts/b01_update_btk.py -y $year -b $basin -p /Users/tsukada/git/realtimeTC/refdata/TCs/tclist.csv -o /Users/tsukada/git/realtimeTC/refdata/TCs/JTWC_pre_btk
done

current_month=$(date +%m)
if [ $current_month -eq 01 ]; then
    lastyear=$((current_year - 1))
    for basin in "${basins[@]}"; do
        python /Users/tsukada/git/realtimeTC/scripts/b01_update_btk.py -y $lastyear -b $basin -p /Users/tsukada/git/realtimeTC/refdata/TCs/tclist.csv -o /Users/tsukada/git/realtimeTC/refdata/TCs/JTWC_pre_btk
    done
fi

rsync -avz /Users/tsukada/git/realtimeTC/outputs/JTWC_pre_intensity/*.png tc-times@www1163.sakura.ne.jp:www/tmp/