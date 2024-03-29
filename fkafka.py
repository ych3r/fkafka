# -*- coding: utf-8 -*-
# fkafka_for_All
# created by liuyc
'''
ref:
    [optparse]
    - https://docs.python.org/3/library/optparse.html
    - https://github.com/ych3r/openssl-tool/blob/main/OpenSSL.py
'''

import re
import datetime
from optparse import OptionParser
import colorama

# put data into list
def data_to_list(file):
    list = []
    try:
        f = open(file, "rb")
    except IOError:
        print("Error: No such file")
    else:
        for line in f:
            list.append(str(line, encoding = "utf-8"))
        f.close()
    return list

# simplify the data
# at some datatime, some process created the other process.
# at some datatime, some process ... the other process.
def deal_with_list(list):
    new_list = []
    # remove last line because it probably is not integrated
    for i in range(len(list) - 1):
        single_event = list[i]
        # get real time
        real_time = re.search(r'"unified_time":(.*?),.*', list[i]).group(1)
        agent_ip = re.search(r'"agent_ip":(.*?),.*', list[i]).group(1)

        # initialize event variable
        event = 0
        md5 = 0

        ################################################################################################
        # general
        if "process_create" in single_event:
            # ppname -> pname
            ppname = re.search(r'"ppname":"(.*?)".*', list[i], re.M|re.I).group(1)
            ppguid = re.search(r'"ppguid":"(.*?)".*', list[i], re.M|re.I).group(1)
            pname = re.search(r'"pname":"(.*?)".*', list[i], re.M|re.I).group(1)
            pguid = re.search(r'"pguid":"(.*?)".*', list[i], re.M|re.I).group(1)
            event = "父进程【" + ppname + "(" + ppguid + ")" + "】创建了子进程【" + pname + "(" + pguid + ")】"

        if "process_access" in single_event:
            #  pname -> dst_pname
            pname = re.search(r'"pname":"(.*?)".*', list[i], re.M|re.I).group(1)
            pguid = re.search(r'"pguid":"(.*?)".*', list[i], re.M|re.I).group(1)
            dst_pname = re.search(r'"dst_pname":"(.*?)".*', list[i], re.M|re.I).group(1)
            dst_pguid = re.search(r'"dst_pguid":"(.*?)".*', list[i], re.M|re.I).group(1)
            event = "进程【" + pname + "(" + pguid + ")" + "】访问了进程【" + dst_pname + "(" + dst_pguid + ")】"
            
        if "net_connect" in single_event:
            # src_ip -> dst_ip
            src_ip = re.search(r'"src_ip":"(.*?)".*', list[i], re.M|re.I).group(1)
            src_port = re.search(r'"src_port":(.*?),.*', list[i], re.M|re.I).group(1)
            dst_ip = re.search(r'"dst_ip":"(.*?)".*', list[i], re.M|re.I).group(1)
            dst_port = re.search(r'"dst_port":(.*?),.*', list[i], re.M|re.I).group(1)
            pname = re.search(r'"pname":"(.*?)".*', list[i], re.M|re.I).group(1)
            pguid = re.search(r'"pguid":"(.*?)".*', list[i], re.M|re.I).group(1)
            event = "进程【" + pname + "(" + pguid + ")" + "】从【" + src_ip + ":" + src_port + "】网络连接到【" + dst_ip + ":" + dst_port + "】"

        if "dns_access" in single_event:
            # pname -> dns_domain
            pname = re.search(r'"pname":"(.*?)".*', list[i], re.M|re.I).group(1)
            pguid = re.search(r'"pguid":"(.*?)".*', list[i], re.M|re.I).group(1)
            dns_domain = re.search(r'"dns_domain":"(.*?)".*', list[i], re.M|re.I).group(1)
            event = "进程【" + pname + "(" + pguid + ")" + "】DNS 访问了【" + dns_domain + "】"

        # if "login" in single_event:
        #     # src_ip
        #     pname = re.search(r'"pname":"(.*?)".*', list[i], re.M|re.I).group(1)
        #     pguid = re.search(r'"pguid":"(.*?)".*', list[i], re.M|re.I).group(1)
        #     src_ip = re.search(r'"src_ip":"(.*?)".*', list[i], re.M|re.I).group(1)
        #     account_name = re.search(r'"account_name":"(.*?)".*', list[i], re.M|re.I).group(1)
        #     tty = re.search(r'"tty":"(.*?)".*', list[i], re.M|re.I).group(1)
        #     event = "用户 " + account_name + " 通过进程【" + pname  + "(" + pguid + ")"+ "】从【" + src_ip + "】登录【" + tty + "】"

        ################################################################################################
        # windows   
        if "ps_create" in single_event:
            # pname
            pname = re.search(r'"pname":"(.*?)".*', list[i], re.M|re.I).group(1)
            pguid = re.search(r'"pguid":"(.*?)".*', list[i], re.M|re.I).group(1)
            event = "创建【" + pname + "(" + pguid + ")" + "】"
            
        if "ps_normal_cmd_execute" in single_event:
            # pname - context
            pname = re.search(r'"pname":"(.*?)".*', list[i], re.M|re.I).group(1)
            pguid = re.search(r'"pguid":"(.*?)".*', list[i], re.M|re.I).group(1)
            context = re.search(r'"context":"(.*?)",.*', list[i], re.M|re.I).group(1)
            event = "【" + pname + "(" + pguid + ")" + "】命令还原为【" + context + "】"
            
        if "ps_input" in single_event:
            # pname - context
            pname = re.search(r'"pname":"(.*?)".*', list[i], re.M|re.I).group(1)
            pguid = re.search(r'"pguid":"(.*?)".*', list[i], re.M|re.I).group(1)
            context = re.search(r'"context":"(.*?)",.*', list[i], re.M|re.I).group(1)
            event = "在【" + pname + "(" + pguid + ")" + "】输入【" + context + "】"
            
        if "ps_script_load" in single_event:
            # pname - script_path
            pname = re.search(r'"pname":"(.*?)".*', list[i], re.M|re.I).group(1)
            pguid = re.search(r'"pguid":"(.*?)".*', list[i], re.M|re.I).group(1)
            script_path = re.search(r'"script_path":"(.*?)",.*', list[i], re.M|re.I).group(1)
            event = "【" + pname + "(" + pguid + ")" + "】引用了脚本【" + script_path + "】"

        if "cmd_input" in single_event:
            # pname - context
            pname = re.search(r'"pname":"(.*?)".*', list[i], re.M|re.I).group(1)
            pguid = re.search(r'"pguid":"(.*?)".*', list[i], re.M|re.I).group(1)
            context = re.search(r'"context":"(.*?)",.*', list[i], re.M|re.I).group(1)
            event = "在【" + pname + "(" + pguid + ")" + "】输入【" + context + "】"
            
            
        if "named_pipe_create" in single_event:
            # pname - pipe_name
            pname = re.search(r'"pname":"(.*?)".*', list[i], re.M|re.I).group(1)
            pguid = re.search(r'"pguid":"(.*?)".*', list[i], re.M|re.I).group(1)
            # linux has different pipe name
            if "\"linux\"" in single_event:
                pipe_name = re.search(r'"fpath":"(.*?)",.*', list[i], re.M|re.I).group(1)
            else:
                pipe_name = re.search(r'"pipe_name":"(.*?)",.*', list[i], re.M|re.I).group(1)
            event = "【" + pname + "(" + pguid + ")" + "】创建了管道【" + pipe_name + "】"
            
        if "named_pipe_connect" in single_event:
            # pname - pipe_connect
            pname = re.search(r'"pname":"(.*?)".*', list[i], re.M|re.I).group(1)
            pguid = re.search(r'"pguid":"(.*?)".*', list[i], re.M|re.I).group(1)
            if "\"linux\"" in single_event:
                pipe_name = re.search(r'"fpath":"(.*?)",.*', list[i], re.M|re.I).group(1)
            else:
                pipe_name = re.search(r'"pipe_name":"(.*?)",.*', list[i], re.M|re.I).group(1)
            event = "【" + pname + "(" + pguid + ")" + "】连接到管道【" + pipe_name + "】"
        
        ################################################################################################
        # linux
        if "bash_audit" in single_event:
            # pname - cmd
            pname = re.search(r'"pname":"(.*?)".*', list[i], re.M|re.I).group(1)
            pguid = re.search(r'"pguid":"(.*?)".*', list[i], re.M|re.I).group(1)
            cmd = re.search(r'"cmd":"(.*?)",.*', list[i], re.M|re.I).group(1)
            event = "[bash]【" + pname + "(" + pguid + ")" + "】执行【" + cmd + "】"

        if "file_symbol_link_create" in single_event:
            # pname - link_fpath
            pname = re.search(r'"pname":"(.*?)".*', list[i], re.M|re.I).group(1)
            pguid = re.search(r'"pguid":"(.*?)".*', list[i], re.M|re.I).group(1)
            link_fpath = re.search(r'"link_fpath":"(.*?)",.*', list[i], re.M|re.I).group(1)
            event = "【" + pname + "(" + pguid + ")" + "】软链接到【" + link_fpath + "】"

        ################################################################################################
        # md5
        if event != 0 and "md5" in single_event:
            md5 = re.search(r'"md5":"(.*?)",.*', list[i]).group(1)
        elif event == 0:
            continue
        elif event != 0 and "md5" not in single_event:
            md5 = ""
        ###############################################################################################
        # add them to new list
        new_list.append([real_time, agent_ip, event])
    return new_list

def sort_by_time(unsorted_list):
    sorted_list = unsorted_list
    sorted_list.sort(key=(lambda x:x[0]))
    # change time type
    for i in sorted_list:
        event_time = datetime.datetime.fromtimestamp(int(i[0]) / 1000).strftime("%Y-%m-%d %H:%M:%S.%f")
        # I noted that the three "0"s on the right are useless.
        i[0] = event_time[:-3]
    return sorted_list

def colorize_list(sorted_list):
    colorama.init(autoreset=True)
    for i in sorted_list:
        i[0] = "\033[1;36m" + i[0] + "\033[0m"
        i[1] = "\033[1;33m" + i[1] + "\033[0m"
    return sorted_list

def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-f", "--file", type = "string", dest = "filename", help = "read kafka data from FILENAME")
    #parser.add_option("-t", "--time", action = "store_true", dest = "time", help = "display time")
    #parser.add_option("-a", "--agent", action = "store_true", dest = "agent", help = "display agent ip")
    #parser.add_option("-m", "--md5", action = "store_true", dest = "md5", help = "display md5")
    parser.add_option("-a", "--all", action = "store_true", dest = "adv", help = "display all")
    
    (options, args) = parser.parse_args()
    file = options.filename
    #time = options.time
    #agent = options.agent
    #md5 = options.md5
    adv = options.adv

    if file != None:
        events_list = deal_with_list(data_to_list(file))
        sorted_list = sort_by_time(events_list)
        sorted_list = colorize_list(sorted_list)

        print('''
              __ _          __ _         
             / _| | ____ _ / _| | ____ _ 
            | |_| |/ / _` | |_| |/ / _` |
            |  _|   < (_| |  _|   < (_| |
            |_| |_|\_\__,_|_| |_|\_\__,_|

                                --- Created by liuyc.

            ''')
        if (adv == True):
            for i in sorted_list:
                if "输入" in i[2]:
                    print("\n\n\n" + i[0], i[1], i[2])
                else:
                    print(i[0], i[1], i[2])
        else:
            for i in sorted_list:
                print(i[2])
        print("\n")
    else:
        print(usage)  

if __name__ == "__main__":
    main()
