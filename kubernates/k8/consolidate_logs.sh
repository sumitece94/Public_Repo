#!/bin/bash
rm consolidated.log

sudo kubectl get pods -A > podsfile.txt
cat podsfile.txt | grep v2v-helper | tr -s ' ' | cut -d' ' -f 2 > pods.txt
cat podsfile.txt | grep migration-controller-manager | tr -s ' ' | cut -d' ' -f 2 >> pods.txt



while read F  ; do
        echo $F
	sudo kubectl logs $F -n migration-system >> consolidated.log
        echo "********** end of $F  logs*************" >> consolidated.log
done < pods.txt

log_timestamp=$(date -r consolidated.log +%m%d%Y%H%M)
cp consolidated.log consolidated-$HOSTNAME-$log_timestamp.log
