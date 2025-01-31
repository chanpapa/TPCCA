import json
import os

import toml
import subprocess
from utils import arg_parser
from utils.area import plot_area
from utils.ccp_parse import bbr_parse
from utils.uniformity_parse_tput_delay import parse_tput_delay, plot_tput_delay
from utils.tools import makefolder
import time
args = arg_parser.argument_parser()
config_file_path = args.config
configs = toml.load(config_file_path)

delay_list = configs['data']['delay_list']
packet_buffer_list = configs['data']['packet_buffer_list']
iteration = configs['data']['iteration']
name_map = configs['data']['plot_name_map']
ccp_algs = configs['data']['ccp_algs']

log_folder = configs['unipath']['log_folder']
fig_folder = configs['unipath']['fig_folder']
trace_folder = configs['path']['trace_folder']
ccp_fig_folder = configs['unipath']['ccp_fig_folder']
mahimahi_fig_folder = configs['unipath']['mahimahi_fig_folder']
area_fig_folder = configs['unipath']['area_fig_folder']
tputwnd=0.13
binsize = 0.25
duration = configs['data']['log']['duration']
enable_iteration_plot = configs['data']['log']['enable_iteration_plot']
enable_alg_plot = configs['data']['log']['enable_alg_plot']

makefolder(fig_folder, ccp_fig_folder)
#makefolder(fig_folder, mahimahi_fig_folder)
makefolder(fig_folder, area_fig_folder)

trace_info = json.load(
    open(os.path.join(trace_folder, 'trace_info.json'), encoding='utf-8'))

print('parse tcpdump pcap file')
for ccp_alg in ccp_algs:
    if ccp_alg !="cubic":
        continue
    for packet_buffer in packet_buffer_list:
        for link_trace in trace_info:
            for delay, delay_var in delay_list:
                delay = int(delay)
                delay_var = round(delay_var, 1)
                for iter_num in range(iteration):
                    
                    t = f'%B\n'
                    log_name = f'{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}'
                    subprocess.run(
                        f'cd {log_folder} && tcptrace -R {log_name}-tcpdump.pcap &&  tcpstat  -o  "%b\n" -r {log_name}-tcpdump.pcap {tputwnd} > {log_name}-tput.txt && cd ..  ',
                        shell=True)
                    time.sleep(2)
                    if os.access(f'./{log_folder}/b2a_rtt.xpl', os.F_OK):
                        old_xpl = f'./{log_folder}/b2a_rtt.xpl'
                    elif os.access(f'./{log_folder}/a2b_rtt.xpl', os.F_OK):
                        old_xpl = f'./{log_folder}/a2b_rtt.xpl'
                    else:
                        continue
                    new_xpl = f'./{log_folder}/{log_name}.txt'
                    
                    os.rename(old_xpl, new_xpl)
                    old_lines = open(f'./{log_folder}/{log_name}.txt', 'r').readlines()
                    rtt_log_name = f'./{log_folder}/{log_name}-rtt.txt'
                    f = open(rtt_log_name, 'w', encoding="utf-8")
                    for line in old_lines:
                        if 'dot' in line:
                            f.write(line[4:])
                    # time(s)and rtt(ms) left
                    f.close()

print('parse mahimahi log')
mahimahi_results = 23

print('plot throughput and delay')
plot_tput_delay(ccp_algs, packet_buffer_list, trace_info, delay_list,
                iteration, mahimahi_results,
                os.path.join(fig_folder, mahimahi_fig_folder), enable_alg_plot,
                enable_iteration_plot,log_folder,tputwnd)
