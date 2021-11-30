timeout 60 sudo tcpdump  -i 'ingress' -s 0 -w "./$1/$2-tcpdump.pcap"  &
sudo iperf3 -c $MAHIMAHI_BASE -p $5 -C $3 -t $4 -i 1 >"./$1/$2-iperf.log"
sleep 1

~                                                                                
~                  
