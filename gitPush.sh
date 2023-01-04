#!/bin/bash
cp ~/env_result.txt ~/Environment_raw_data
cd /Environment_raw_data
d=`date "+%F"` #全体をバッククォートで囲む
echo $d
git add env_result.txt
git commit -m $d
git push origin main
