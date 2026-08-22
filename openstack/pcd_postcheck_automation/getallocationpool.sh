#!/bin/bash

while read F  ; do
        echo $F
	openstack subnet show $F -f value -c allocation_pools
        echo "********** end of $F  logs*************" 
done < $1
