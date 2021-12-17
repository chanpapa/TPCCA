#!/usr/bin/python3

import os
import subprocess
import re
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from pathlib import Path
from utils import tools

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


def get_throughput_data(fn):
    cmd = "grep ' + ' {} | awk '{{print $1, $3}}'".format(fn)
    res = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    cmd2 = "grep '# base timestamp' {} | awk '{{print $4}}'".format(fn)
    bt = subprocess.run(cmd2, stdout=subprocess.PIPE, shell=True)
    bt = bt.stdout.decode("utf-8").split('\n')[0]
    for l in res.stdout.decode("utf-8").split('\n'):
        sp = l.split(" ")
        if len(sp) != 2:
            continue
        t, v = sp
        yield float(int(t) - int(bt)) / 1e3, float(v)


def get_delay_data(fn):
    cmd = "grep ' - ' {} | awk '{{print $1, $4}}'".format(fn)
    res = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    cmd2 = "grep '# base timestamp' {} | awk '{{print $4}}'".format(fn)
    bt = subprocess.run(cmd2, stdout=subprocess.PIPE, shell=True)
    bt = bt.stdout.decode("utf-8").split('\n')[0]
    for l in res.stdout.decode("utf-8").split('\n'):
        sp = l.split(" ")
        if len(sp) != 2:
            continue
        t, v = sp
        yield float(int(t) - int(bt)) / 1e3, float(v)


def get_throughput(data, start_time, end_time, binsize=0):
    bin_start = start_time
    last_t = start_time
    current_bin_tput = 0
    for t, p in data:
        if t < start_time:
            continue
        if t > end_time:
            break
        if t > (bin_start + binsize):  # start new bin
            yield bin_start, current_bin_tput / (t - bin_start)
            bin_start = t
            current_bin_tput = p * 8.0
        else:
            current_bin_tput += p * 8.0
            last_t = t


def get_delays(data, bin_times):
    # this function is not used but left here in case to be used
    next_bin = next(bin_times)
    delays = []
    for t, p in data:
        if t < next_bin:
            delays.append(p)
        else:
            if len(delays) > 0:
                yield np.mean(delays)
            else:
                yield 0
            delays = []
            delays.append(p)
            next_bin = next(bin_times)

    yield np.mean(delays)


def get_times(fn, binsize):
    bin_start = 0
    yield 0
    for t, _ in get_throughput_data(fn):
        if (bin_start + binsize) > t:
            yield t
    yield t


def get_expt_data(fn, duration, binsize=0):
    tp = get_throughput_data(fn)
    td = get_delay_data(fn)
    ts, tp = zip(*get_throughput(tp, 0, duration, binsize))
    ts = list(ts)
    dl = get_delays(td, iter(ts))
    return zip(ts, tp, dl)


# filename: <alg>-<bw>-<bw_scenario>-<delay>-<delay_var>-mahimahi.log
def binAlgs(fns):
    '''
    Parse filename.

    Args:
        fns (list): each element is a file name. <alg>-<bw>-<bw_scenario>-<delay>-<delay_var>-mahimahi.log

    Returns:
        dict: file infos
    '''
    plots = {}
    for fn in fns:
        sp = fn.split('-')
        if sp[-1] != "mahimahi.log":
            continue
        alg, bw, bw_seq, packet_buf, delay, delay_var, iter_num = sp[:-1]
        pl = (alg, bw, bw_seq, packet_buf, delay, delay_var, iter_num)
        if pl in plots:
            plots[pl].append(fn)
        else:
            plots[pl] = [fn]
    return plots


def parse_tput_delay(log_folder, duration, binsize=0):
    '''
    Parse throughput and delay. (delay is not used yet)

    Args:
        log_folder (str): folder of raw logs
        duration (int or float): duration of time sequence
        binsize (int, optional): binsize of throughput time interval. Defaults to 0.

    Returns:
        dict: time sequence, throughput sequence and delay sequence of log files.
    '''
    exps = binAlgs(sorted(os.listdir(log_folder)))
    results = {}

    print('Parse Throughput and Delay...')
    for exp in tqdm(exps):
        time_list = []
        tput_list = []
        dl_list = []
        myfile = Path(os.path.join(log_folder, exps[exp][0]))
        flag = 0
        if myfile.exists():
            flag = 1
            for t, tput, dl in get_expt_data(
                    os.path.join(log_folder, exps[exp][0]),
                    min(duration, 2 * float(exp[4])),
                    binsize):
                time_list.append(t)
                tput_list.append(tput / 1000 / 1000)
                dl_list.append(dl)
        results[exps[exp][0]] = {
            'flag': flag,
            'time_list': time_list,
            "tput_list": tput_list,
            "dl_list": dl_list
        }
    return results


def restrict(a, b, c):
    if abs(a - b) <= c:
        return True
    else:
        return False


def plot_tput_delay(ccp_algs,
                    packet_buffer_list,
                    trace_info,
                    delay_list,
                    iteration,
                    mahimahi_results,
                    fig_folder,
                    enable_alg_plot=False,
                    enable_iteration_plot=False, log_folder=f"uni_slog",tputwnd=0.25):
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
    tools.clear_folder(fig_folder)
    print('Plot Throughput and Delay...')
    if enable_alg_plot:
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
            plt.close()
    pbar = tqdm(total=len(packet_buffer_list) * len(trace_info) *
                      len(delay_list) * iteration)
    for packet_buffer in packet_buffer_list:
        for link_trace in trace_info:
            for delay, delay_var in delay_list:
                delay = int(delay)
                delay_var = round(delay_var, 1)
                plt.figure(figsize=(6.4, 3))
                count = 0
                XMAX = int(53/tputwnd)
                wnd = 0.25
                for ccp_alg in ccp_algs:
               
                    tl = np.zeros((300, 2), dtype=np.float)
                    tpl = np.zeros((iteration, int(65 / wnd), 2,), dtype=np.float)
                    for iter_num in range(iteration):
                        xmax = int(52/tputwnd)
                        lines = open(f'./{log_folder}/{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-tput.txt', 'r').readlines()
                        count=0
                        tput_list=[]
                        time_list=[]
                        for line in lines:
                            a=float(line)/1000/1000
                            if count >XMAX:
                                break
                            tput_list.append(a)
                            time_list.append((count+1)*tputwnd)
                            count+=1    
                        start = 0
                        b = re.findall(r'\d+', link_trace)
                        b = float(b[0])
                        for i in range(count-2):
                            a = int(time_list[i] / wnd)
                            if a < 6.0 / wnd:
                                tl[a][0] += tput_list[i]
                                tl[a][1] += 1
                                tpl[iter_num][a][0] += tput_list[i]
                                tpl[iter_num][a][1] += 1
                                continue
                            if restrict(a, 10.0 / wnd, (6.0 / wnd) + 1) or restrict(a, (20.0 / wnd), (10 / wnd)):
                                tl[a][0] += tput_list[i]
                                tl[a][1] += 1
                                tpl[iter_num][a][0] += tput_list[i]
                                tpl[iter_num][a][1] += 1
                                continue
                            if restrict(tput_list[i], b, 0.5 * b) and a < 20 / wnd:
                                tl[a][0] += tput_list[i]
                                tl[a][1] += 1
                                tpl[iter_num][a][0] += tput_list[i]
                                tpl[iter_num][a][1] += 1
                                continue
                            if  tput_list[i] > b and a < 50 / wnd:
                                tl[a][0] += tput_list[i]
                                tl[a][1] += 1
                                tpl[iter_num][a][0] += tput_list[i]
                                tpl[iter_num][a][1] += 1
                                continue
                    xl = np.zeros((600,), dtype=np.float)
                    yl = np.zeros((600,), dtype=np.float)
                    for i in range(int(64 / wnd)):
                        if tl[i][1] != 0:
                            yl[i] = tl[i][0] / tl[i][1]
                        for t in range(iteration):
                            if tpl[t][i][1] != 0:
                                tpl[t][i][0] = tpl[t][i][0] / tpl[t][i][1]
                    tlpercent15 = []
                    tlpercent25 = []
                    tlpercent75 = []
                    tlpercent95 = []
                    for i in range(int(53 / wnd)):
                        zq = np.zeros((iteration), dtype=np.float)
                        for t in range(iteration):
                            zq[t] = tpl[t][i][0]
                        tlpercent15.append(np.percentile(zq, 15))
                        tlpercent25.append(np.percentile(zq, 25))
                        tlpercent75.append(np.percentile(zq, 75))
                        tlpercent95.append(np.percentile(zq, 95))
                    for i in range(len(tl)):
                        xl[i] = wnd * i
                    XMAX = int(50 / wnd)
                    plt.plot(xl[0:XMAX], yl[0:XMAX], label=f'mean')
                    plt.plot(xl[0:XMAX], tlpercent15[0:XMAX], label=f'15%')
                    plt.plot(xl[0:XMAX], tlpercent25[0:XMAX], label=f'25%')
                    plt.plot(xl[0:XMAX], tlpercent75[0:XMAX], label=f'75%')
                    plt.plot(xl[0:XMAX], tlpercent95[0:XMAX], label=f'95%')
                    plt.xlabel('Time (s)', fontsize='12')
                    plt.ylabel('Throughput (Mbps)', fontsize='12')
                    plt.legend()
                    plt.savefig(os.path.join(
                        fig_folder,
                        f'uniformity-{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-mahimahi.png'
                    ),
                        bbox_inches='tight')
                    plt.close()
                    
                # RTT uniformity
                rttwnd = 0.2
                for ccp_alg in ccp_algs:
                    tl = np.zeros((300, 2), dtype=np.float)
                    rpl = np.zeros((iteration, int(60 /rttwnd),), dtype=np.float)
                    iterseq=0
                    for iter_num in range(iteration):
                        xmax = 0
                        time_list = []
                        rtt_list = []
                        instant_time_List = []
                        instant_rtt_List = []
                        time_wnd = np.array([])
                        rtt_wnd = np.array([])
                        avg_rtt = np.array([])
                        if not os.access(f'./{log_folder}/{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-rtt.txt', os.F_OK):
                            continue
                        iterseq+=1
                        lines = open(
                            f'./{log_folder}/{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-rtt.txt',
                            'r').readlines()
                        initial_time = float(re.findall(r'\d+(?:\.\d+)?', lines[0])[0])
                        for line in lines:
                            a = re.findall(r'\d+(?:\.\d+)?', line)
                            time = float(a[0]) - initial_time
                            rtt = int(a[1])
                            if len(time_wnd) == 0:
                                time_wnd = np.append(time_wnd, time)
                                rtt_wnd = np.append(rtt_wnd, rtt)
                                continue
                            if int(time/rttwnd)==int(time_wnd[0]/rttwnd): #在同一个区间
                                time_wnd = np.append(time_wnd, time)
                                rtt_wnd = np.append(rtt_wnd, rtt)
                                continue
                            time_list.append((int(time_wnd[0]/rttwnd)+1)*rttwnd)
                            rtt_list.append(np.mean(rtt))
                            time_wnd = np.array([])
                            rtt_wnd = np.array([])
                            time_wnd = np.append(time_wnd, time)
                            rtt_wnd = np.append(rtt_wnd, rtt)
                        for j in range(len(time_list)):
                            rpl[iterseq-1][j] = rtt_list[j]
                    xl = np.zeros((600,), dtype=np.float)
                    yl = np.zeros((600,), dtype=np.float)
                    tlpercent15 = []
                    tlpercent25 = []
                    tlpercent75 = []
                    tlpercent95 = []
                    mymax=len(rtt_list)-5
                    for i in range(mymax):
                        zq = np.zeros((iteration), dtype=np.float)
                        for t in range(iterseq):
                            zq[t] = rpl[t][i]
                        tlpercent15.append(np.percentile(zq, 15))
                        tlpercent25.append(np.percentile(zq, 25))
                        tlpercent75.append(np.percentile(zq, 75))
                        tlpercent95.append(np.percentile(zq, 95))
                    for i in range(len(tl)):
                        xl[i] = rttwnd * i
                    XMAX = int(mymax-1)
                    plt.plot(xl[0:XMAX], yl[0:XMAX], label=f'mean')
                    plt.plot(xl[0:XMAX], tlpercent15[0:XMAX], label=f'15%')
                    plt.plot(xl[0:XMAX], tlpercent25[0:XMAX], label=f'25%')
                    plt.plot(xl[0:XMAX], tlpercent75[0:XMAX], label=f'75%')
                    plt.plot(xl[0:XMAX], tlpercent95[0:XMAX], label=f'95%')
                    plt.xlabel('Time (s)', fontsize='12')
                    plt.ylabel('RTT (ms)', fontsize='12')
                    plt.legend()
                    plt.savefig(os.path.join(
                        fig_folder,
                        f'uniformity-{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-RTT.png'
                    ),
                        bbox_inches='tight')
                    plt.close()
                    pbar.update(1)
    pbar.close()
    # plot varience figure


'''
                fig,ax = plt.subplots(figsize=(25, 14))
                ax.legend()
                crh=0
                for ccp in ccp_algs:
                    crh+=1
                    stat=np.zeros((350,2,150), dtype=np.float)
                    statplot=np.array([])
                    wnd=0.5
                    loc=np.zeros((300,1), dtype=np.int)
                    for iter_num in range(iteration):                   
                        last=0
                        log_name = f'{ccp}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-mahimahi.log'
                        try:
                            xmax=len(mahimahi_results[log_name]['time_list'])
                            print('wrong')
                        except :
                            continue
                        for i in range(xmax-10):                     
                            a=int(time_list[i]/wnd+1)
                            if not (restrict(a,10.0/wnd,(6.0/wnd)+1) or restrict(a,(20.0/wnd),(10.0/wnd))):
                            if not(restrict(mahimahi_results[log_name]['tput_list'][i],b,12) and a< 20/wnd) :
                            if not(restrict(mahimahi_results[log_name]['tput_list'][i],2*b,30) and a< 40/wnd) :
                                continue
                            stat[a][0][loc[a][0]]+=mahimahi_results[log_name]['tput_list'][i]
                            stat[a][1][loc[a][0]]+=1
                            if last < a:
                                loc[a][0]+=1   #相应区间的点的数量
                                last=a
                        for a in range(XMAX):
                            for i in range(loc[a][0]+1):
                                if stat[a][1][i] !=0:
                                stat[a][0][i]=stat[a][0][i]/stat[a][1][i]
                                statplot=np.append(statplot,np.var(stat[a][0][0:loc[a][0]]))            
                        xticks=np.arange(XMAX)
                        if crh ==1 :
                            ax.bar(xticks[40:60], statplot[40:60], width=0.25, label=f'{ccp}', color="blue")
                        else :
                            ax.bar(xticks[40:60]+0.25, statplot[40:60], width=0.25, label=f'{ccp}', color="red")
                            ax.set_xticks(xticks[40:60]+0.125)
                        xticklabels=[]
                for i in range(XMAX):
                  xticklabels.append(str(wnd*i)+"-"+str(wnd*i+wnd)+'s')
                ax.set_xticklabels(xticklabels[39:59])    
                plt.xlabel('Time (s)', fontsize='12')
                plt.ylabel('Varience', fontsize='12')
                plt.legend()
                plt.savefig(os.path.join(
                        fig_folder,
                f'var-nonzero-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-mahimahi.png'
                ),
                bbox_inches='tight')
                plt.close()

    pbar.close()
    if iteration > 1 and enable_iteration_plot:
        pbar = tqdm(total=len(packet_buffer_list) * len(trace_info) *
                    len(delay_list) * iteration)
        for packet_buffer in packet_buffer_list:
            for link_trace in trace_info:
                for delay, delay_var in delay_list:
                    delay = int(delay)
                    delay_var = round(delay_var, 1)
                    for ccp_alg in ccp_algs:
                        plt.figure(figsize=(6.4, 3))
                        for iter_num in range(iteration):
                            log_name = f'{ccp_alg}-{link_trace}-{delay}-{delay_var}-{iter_num}-mahimahi.log'
                            plt.plot(
                                mahimahi_results[log_name]['time_list'],
                                mahimahi_results[log_name]['tput_list'],
                                label=f'{iter_num}')
                        # plt.title(f'{ccp_alg}-{link_trace}-{delay}-{delay_var}-mahimahi')
                        plt.xlabel('Time (s)', fontsize='12')
                        plt.ylabel('Throughput (Mbps)', fontsize='12')
                        plt.legend()
                        plt.savefig(os.path.join(
                            fig_folder,
                            f'iter-{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-mahimahi.png'
                        ),
                                    bbox_inches='tight')
                        plt.close()
                        pbar.update(1)
        pbar.close()
'''
