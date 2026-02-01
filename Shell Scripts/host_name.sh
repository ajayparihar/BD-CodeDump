#!/bin/bash

# Define arrays for different environments with custom hostnames
supArray=("customHost1" "customHost2" "customHost3")
prodArray=("customProd1" "customProd2" "customProd3")
arr3=("customArr3host1" "customArr3host2")
arr4=("customArr4host1" "customArr4host2")

# Get the current hostname and save it to the variable hostName
hostName=$(hostname)

# Check which array the hostname belongs to and SSH to the corresponding custom host
if [[ " ${supArray[@]} " =~ " ${hostName} " ]]; then
    echo "$hostName is in supArray"
    ssh customHost1  # Replace customHost1 with the host you want to SSH into

elif [[ " ${prodArray[@]} " =~ " ${hostName} " ]]; then
    echo "$hostName is in prodArray"
    ssh customProd1  # Replace customProd1 with the host you want to SSH into

elif [[ " ${arr3[@]} " =~ " ${hostName} " ]]; then
    echo "$hostName is in arr3"
    ssh customArr3host1  # Replace with customArr3host1

elif [[ " ${arr4[@]} " =~ " ${hostName} " ]]; then
    echo "$hostName is in arr4"
    ssh customArr4host1  # Replace with customArr4host1

else
    echo "$hostName is not in any of the defined arrays"
fi
