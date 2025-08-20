#! /usr/bin/bash

terms="2S 3S AS BS FA JA SP"
# 0405 0506 0607 0708 0809 0910 1011 1112 1213 1314
years="1314 1415 1516 1617 1718 1819 1920 2021 2122 2223 2324"
folder="Education materials backups"
prefixes="EDU"

for prefix in ${prefixes} ; do
    for year in ${years} ; do
        for term in ${terms} ; do
            echo rclone move \'PHB-Converse-GDrive:DEd/course-backups/${folder}/${prefix}\' PHB-Converse-GDrive:DEd/course-backups/${year}-${term} --include \"${year}-${term}*\"
            rclone move "PHB-Converse-GDrive:DEd/course-backups/${folder}/${prefix}" PHB-Converse-GDrive:DEd/course-backups/${year}-${term} --include "${year}-${term}*"
        done
    done
done