#!/bin/bash

create_file() {
    file_name="testFile_${i}.junk"
    echo "creating file: ${file_name}"
    dd if=/dev/urandom of=$file_name  bs=1048576  count=$size
}

#dd if=/dev/urandom of=testFile_2  bs=10240  count=10240
#dd if=/dev/urandom of=testFile_3  bs=10240  count=10240
#dd if=/dev/urandom of=testFile_4  bs=10240  count=10240
#cp testFile_4 testFile_5

i="0"
size=$2
while [ $i -lt $1 ]
do
    create_file & i=$[$i+1]
done

while [ true ]
do
    ls -lh
    sleep 1
done