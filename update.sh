#!/bin/sh

source venv/bin/activate
packages=$(pip list -o | awk '{print $1;}')
counter=0
for package in ${packages[@]};
do
    if [ $counter != 0 ] && [ $counter != 1 ]; then
        pip install $package -U
        read -n 1 -p "Confirm package update? [y/n]" confirm
        echo -e "\n"
        while [ $confirm != "y" ] && [ $confirm != "n" ];
        do
            read -n 1 -p "Enter [y/n]" confirm
        done
        if [ $confirm == "y" ]; then
            pip freeze > requirements.txt
        fi
        pip install -r requirements.txt &> /dev/null
    fi
    ((counter++))
done
deactivate