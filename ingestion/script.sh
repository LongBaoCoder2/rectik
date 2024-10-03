#!/bin/bash

main_file="./flows/data_ingestion_flow.py"

python3 $main_file run

if [ $? -eq 0 ]; then
    echo "Script executed successfully."
else
    echo "Script failed to execute."
fi