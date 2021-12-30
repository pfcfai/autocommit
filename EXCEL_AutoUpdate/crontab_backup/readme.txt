因為batch.sh 會跑所有資料夾底下的py檔 技術還不到位 不會寫 exclude
所以先把不適合批次更新的py檔移轉到 crontab_backup 底下
避免像 UpdateOI_MySQL.py 這種時間到了跑才不會出空值的程式碼
