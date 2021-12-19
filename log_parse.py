import json
import os
import os.path
import time
import toml
import subprocess
from utils import arg_parser
from utils.area import plot_area
from utils.ccp_parse import bbr_parse
from utils.parse_rtt import plot_tput_delay
from utils.tools import makefolder,clear_folder
import re
args = arg_parser.argument_parser()
config_file_path = args.config
configs = toml.load(config_file_path)

delay_list = configs['data']['delay_list']
packet_buffer_list = configs['data']['packet_buffer_list']
iteration = configs['data']['iteration']
name_map = configs['data']['plot_name_map']
ccp_algs = configs['data']['ccp_algs']

log_folder = configs['path']['log_folder']
fig_folder = configs['path']['fig_folder']
trace_folder = configs['path']['trace_folder']
ccp_fig_folder = configs['path']['ccp_fig_folder']
mahimahi_fig_folder = configs['path']['mahimahi_fig_folder']
area_fig_folder = configs['path']['area_fig_folder']

binsize = configs['data']['log']['binsize']
duration = configs['data']['log']['duration']
enable_iteration_plot = configs['data']['log']['enable_iteration_plot']
enable_alg_plot = configs['data']['log']['enable_alg_plot']
clear_folder(fig_folder)
makefolder(fig_folder, ccp_fig_folder)
makefolder(fig_folder, mahimahi_fig_folder)
makefolder(fig_folder, area_fig_folder)
tputwnd=0.3
trace_info = json.load(
    open(os.path.join(trace_folder, 'trace_info.json'), encoding='utf-8'))

# mahimahi_results = json.load(open('tmp/mahimahi_results.json'))

print('parse tcpdump pcap file')
for ccp_alg in ccp_algs:
    for packet_buffer in packet_buffer_list:
        for link_trace in trace_info:
            for delay, delay_var in delay_list:
                delay = int(delay)
                delay_var = round(delay_var, 1)
                for iter_num in range(iteration):
                    log_name = f'{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}'
                    rttalgorithm1="AVG(tcp.analysis.ack_rtt)tcp.analysis.ack_rtt"
                    rttalgorithm2="MIN(tcp.analysis.ack_rtt)tcp.analysis.ack_rtt"
                    rttalgorithm3="MAX(tcp.analysis.ack_rtt)tcp.analysis.ack_rtt"
                    if os.access(f'./{log_folder}/{log_name}.txt',os.F_OK):
                        continue
                    subprocess.run(
                        f'cd {log_folder} &&  tshark -r {log_name}-tcpdump.pcap   -q -z io,stat,0.3s,"{rttalgorithm1}","{rttalgorithm2}","{rttalgorithm3}">{log_name}.txt &&  tcpstat  -o  "%b\n" -r {log_name}-tcpdump.pcap {tputwnd} > {log_name}-tput.txt && cd ..  ',
                        shell=True)
                    time.sleep(2)
                    old_lines = open(f'./{log_folder}/{log_name}.txt', 'r').readlines()
                    rtt_log_name = f'./{log_folder}/{log_name}-rtt.txt'
                    f = open(rtt_log_name, 'w', encoding="utf-8")
                    for line in old_lines:
                        if "<>" not in line:
                            continue
                        newline=re.findall(r"[-+]?\d*\.\d+|\d+", line)
                        f.write(f"{newline[1]} {newline[2]}\n")
                    # time(s)and rtt(ms) left
                    f.close()

print('plot rtt and tput')
mahimahi_results = 23  # whatever
plot_tput_delay(ccp_algs, packet_buffer_list, trace_info, delay_list,
                iteration, mahimahi_results,
                os.path.join(fig_folder, mahimahi_fig_folder), enable_alg_plot,
                enable_iteration_plot,tputwnd)
'''
print('parse mahimahi log and ')
area_dict = plot_area(ccp_algs, packet_buffer_list, trace_info, delay_list,
                      iteration, mahimahi_results,
                      os.path.join(fig_folder, area_fig_folder), name_map)
'''
