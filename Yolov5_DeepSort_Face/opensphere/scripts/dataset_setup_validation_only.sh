#!/bin/bash

if [ ! -d "data" ]; then
  mkdir data
fi
cd data

if [ ! -d "test" ]; then
  mkdir test
fi
if [ ! -d "val" ]; then
  mkdir val
fi

cd test
wget https://owncloud.tuebingen.mpg.de/index.php/s/qw4xLwBiFSLwEBk/download -O IJB.tar
tar xvf IJB.tar
rm IJB.tar
cd ../val
wget https://owncloud.tuebingen.mpg.de/index.php/s/wTNTz8RtZ8DKRPJ/download -O validation.tar
tar xvf validation.tar
rm validation.tar

