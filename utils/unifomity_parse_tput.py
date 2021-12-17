#!/usr/bin/python3

import os
import subprocess
import re
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import subprocess
from utils import tools

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

def plot_tput_delay(ccp_algs,
                    packet_buffer_list,
                    trace_info,
                    delay_list,
                    iteration,
                    mahimahi_results,
                    fig_folder,
                    enable_alg_plot=False,
                    enable_iteration_plot=False,tputwnd=0.2):
    '''
    Plot throughput and delay(delay plot not implemented yet).

    Args:
        ccp_algs (dict): CCP algorithms dict
        packet_buffer_list (list): packet buffer list
        trace_info (dict): traces information
        delay_list (list): delay list
        iteration (int): number of iterations
        mahimahi_results (dict): parsed mahimahi log
        fig_folder (str): folder to save figures
        enable_alg_plot (bool, optional): if plot every algorithm. Defaults to False.
        enable_iteration_plot (bool, optional): if plot every iteration. Defaults to False.
    '''
   

    #tools.clear_folder(fig_folder)
    iteration=10
    print('Plot Throughput and Delay...')
    '''if enable_alg_plot:
        for res in tqdm(mahimahi_results):
            plt.figure(figsize=(6.4, 3))
            plt.plot(mahimahi_results[res]['time_list'],
                     mahimahi_results[res]['tput_list'],
                     'ro-',
                     label='Throughput')
            # plt.title(res)
            plt.xlabel('Time (s)', fontsize='12')
            plt.ylabel('Throughput (Mbps)', fontsize='12')
            plt.legend()
            plt.savefig(os.path.join(fig_folder, res[:-4] + '.png'),
                        bbox_inches='tight')
            plt.close()'''
 
    pbar = tqdm(total=len(packet_buffer_list) * len(trace_info) *
                len(delay_list) * iteration)
    for packet_buffer in packet_buffer_list:
        for link_trace in trace_info:
            for delay, delay_var in delay_list:
                delay = int(delay)
                delay_var = round(delay_var, 1)
                for iter_num in range(iteration):
                    plt.figure(figsize=(12, 5))
                    for ccp_alg in ccp_algs:
                        log_name = f'{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-mahimahi.log'
                        time_list=[]
                        tput_list=[]
                        avg_tput=np.array([])   
                        lines = open(f'./log/{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-tput.txt', 'r').readlines()
                        time=0
                        for line in lines:
                          a=float(line)/1000/1000
                          tput_list.append(a)
                          time+=tputwnd
                          time_list.append(time)
                        plt.plot(
                            time_list[0:int(75/tputwnd)],
                            tput_list[0:int(75/tputwnd)],
                            label=f'{ccp_alg}')
                    plt.title(f'bwstep-diff-{link_trace}-{delay}-{delay_var}-tputlongterm')
                    plt.xlabel('Time (s)', fontsize='12')
                    plt.ylabel('Throughput (Mbps)', fontsize='12')
                    plt.legend()
                    plt.savefig(os.path.join(
                        fig_folder,
                        f'bwstep-diff-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-longtermtput.png'
                    ),
                                bbox_inches='tight')
                    plt.close()
                    plt.figure(figsize=(12, 5))
                    
                    '''for ccp_alg in ccp_algs:
                        log_name = f'{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-mahimahi.log'
                        time_list=[]
                        tput_list=[]
                        avg_tput=np.array([])   
                        lines = open(f'./log/{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-tput.txt', 'r').readlines()
                        time=0
                        for line in lines:
                            a=re.findall(r'\d+(?:\.\d+)?', line)
                            time=time+0.01
                            tput=float(a[0])/1000/1000
                            if time<13:
                                continue
                            if time>=17:
                                break
                            if time >15 and time <43:
                                avg_tput=np.append(avg_tput,tput)   
                            time_list.append(time)
                            tput_list.append(tput)
                        plt.plot(
                            time_list,
                            tput_list,
                            label=f'{ccp_alg}_avg={np.mean(avg_tput)}ms')
                    plt.title(f'uprttdiff-{link_trace}-{delay}-{delay_var}-longterm')
                    plt.xlabel('Time (s)', fontsize='12')
                    plt.ylabel('Throughput (Mbps)', fontsize='12')
                    plt.legend()
                    plt.savefig(os.path.join(
                        fig_folder,
                        f'uprttdiff-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-shorttermtput.png'
                    ),
                                bbox_inches='tight')
                    plt.close()
                    plt.figure(figsize=(12, 5))'''
#plot rtt in long term
                    for ccp_alg in ccp_algs:
                        log_name = f'{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-mahimahi.log'
                        time_list=[]
                        rtt_list=[]
                        instant_time_List=[]
                        instant_rtt_List=[]
                        time_wnd=np.array([])
                        rtt_wnd=np.array([])
                        avg_rtt=np.array([])   
                        lines = open(f'./log/{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-rtt.txt', 'r').readlines()
                        initial_time=float(re.findall(r'\d+(?:\.\d+)?', lines[0])[0])
                        for line in lines:
                            a=re.findall(r'\d+(?:\.\d+)?', line)
                            time=float(a[0])-initial_time
                            rtt=int(a[1])
                            if time>=75:
                                break
                            if  time <17:
                                instant_time_List.append(time-13)
                                instant_rtt_List.append(rtt) 
                            if time >=35 and time <75:
                                avg_rtt=np.append(avg_rtt,rtt)   
                            if len(time_wnd)==0:    
                                time_wnd=np.append(time_wnd,time)
                                rtt_wnd=np.append(rtt_wnd,rtt)
                            if time-time_wnd[0]<0.2:
                                time_wnd=np.append(time_wnd,time)
                                rtt_wnd=np.append(rtt_wnd,rtt)
                                continue
                            time_list.append(np.mean(time_wnd))
                            rtt_list.append(np.mean(rtt))
                            time_wnd=np.array([])
                            rtt_wnd=np.array([])
                            time_wnd=np.append(time_wnd,time)
                            rtt_wnd=np.append(rtt_wnd,rtt) 
                        plt.plot(
                            time_list,
                            rtt_list,
                            label=f'{ccp_alg}_avg={np.mean(avg_rtt)}ms')
                    plt.title(f'bwstep-diff-{link_trace}-{delay}-{delay_var}-longtermRTT')
                    plt.xlabel('Time (s)', fontsize='12')
                    plt.ylabel('RTT (ms)', fontsize='12')
                    plt.legend()
                    plt.savefig(os.path.join(
                        fig_folder,
                        f'bwstep-diff-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-longtermRTT.png'
                    ),
                                bbox_inches='tight')
                    plt.close()
                    pbar.update(1)
                    #plot instant rtt timing figures
                    '''for ccp_alg in ccp_algs:
                        log_name = f'{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-mahimahi.log'
                        instant_time_List=[]
                        instant_rtt_List=[] 
                        lines = open(f'./log/{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-rtt.txt', 'r').readlines()
                        initial_time=float(re.findall(r'\d+(?:\.\d+)?', lines[0])[0])
                        for line in lines:
                            a=re.findall(r'\d+(?:\.\d+)?', line)
                            time=float(a[0])-initial_time
                            rtt=int(a[1])
                            if time<12:
                                continue
                            if time>=17:
                                break
                            if time>13 and time <17:
                                instant_time_List.append(time-13)
                                instant_rtt_List.append(rtt) 
                        plt.plot(
                            instant_time_List,
                            instant_rtt_List,
                            label=f'{ccp_alg}')
                    plt.title(f'uprttdiff-{link_trace}-{delay}-{delay_var}-shorttermRTT')
                    plt.xlabel('Time (s)', fontsize='12')
                    plt.ylabel('RTT (ms)', fontsize='12')
                    plt.legend()
                    plt.savefig(os.path.join(
                        fig_folder,
                        f'uprttdiff-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-shorttermRTT.png'
                    ),
                                bbox_inches='tight')
                    plt.close()
                    plt.figure(figsize=(12, 5))
                    #down
                    for ccp_alg in ccp_algs:
                        log_name = f'{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-mahimahi.log'
                        time_list=[]
                        rtt_list=[]
                        time_wnd=np.array([])
                        rtt_wnd=np.array([])
                        lines = open(f'./log/{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-rtt.txt', 'r').readlines()
                        initial_time=float(re.findall(r'\d+(?:\.\d+)?', lines[0])[0])
                        for line in lines:
                            a=re.findall(r'\d+(?:\.\d+)?', line)
                            time=float(a[0])-initial_time
                            rtt=int(a[1])
                            if time<=42:
                                continue
                            if time>59:
                                break
                            if len(time_wnd)==0:    
                                time_wnd=np.append(time_wnd,time-42)
                                rtt_wnd=np.append(rtt_wnd,rtt)
                            if time-time_wnd[0]<0.01:
                                time_wnd=np.append(time_wnd,time-42)
                                rtt_wnd=np.append(rtt_wnd,rtt)
                                continue
                            time_list.append(np.mean(time_wnd))
                            rtt_list.append(np.mean(rtt))
                            time_wnd=np.array([])
                            rtt_wnd=np.array([])
                            time_wnd=np.append(time_wnd,time-42)
                            rtt_wnd=np.append(rtt_wnd,rtt)  
                        plt.plot(
                            time_list,
                            rtt_list,
                            label=f'{ccp_alg}')
                    # plt.title(f'{link_trace}-{delay}-{delay_var}-mahimahi')
                    plt.xlabel('Time (s)', fontsize='12')
                    plt.ylabel('RTT (ms)', fontsize='12')
                    plt.legend()
                    plt.savefig(os.path.join(
                        fig_folder,
                        f'downrttdiff-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-longtermRTT.png'
                    ),
                                bbox_inches='tight')
                    plt.close()

                    pbar.update(1)'''
    pbar.close()
