timeout 60 sudo tcpdump  -i 'ingress' -s 0 -w "./$1/$2-tcpdump.pcap"  &
sudo iperf -c $MAHIMAHI_BASE -p $5 -Z $3 -t $4 -i 1 >"./$1/$2-iperf.log"
sleep 1

~                                                                                
~                  
