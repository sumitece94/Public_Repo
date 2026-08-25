subnets=$(openstack subnet list -f value -c Subnet)
while read -r IP; do
	subnet_found=""
	echo "checking ip: $IP"
	ping -a $IP -c 3
        for i in $subnets; do 
		grepcidr "$i" <(echo "$IP") > /dev/null 2>&1; 
		if [ $? -eq 0 ]; then 
			subnet_found=$i; 
			break; 
		fi; 
	done
	echo "$IP belongs to $subnet_found"
done < "$IP_FILE"
