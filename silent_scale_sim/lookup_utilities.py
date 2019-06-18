import subprocess as sp
import os

#db_home = "/usr/scratch2/anand/silent_scale_sim/replay_mem/"
db_home = "/home/anand/repos/fccm_scale_runs/silent_scale_sim/replay_mem/"
dirfilename= "lookup_table.csv"

def lookup(tag):
    hit_flag = False
    dirname = ""

    dirfile = db_home + dirfilename 
    f = open(dirfile, 'r')

    for row in f:
        elem = row.strip().split(',')
        key = elem[0].strip()

        if key == tag:
            dirname = elem[1].strip()
            hit_flag = True
    
    f.close()
    return hit_flag, dirname


def get_sram_stats(dirname, dest_dir):
    # Copy the run files to the dest
    # Read the details file and copy the sram and util
    cmd = "ln -s " + dirname + '/*.csv ' + dest_dir + "/"
    os.system(cmd)

    cmd = "rm -rf " + dest_dir +"/sram_stats.csv"
    os.system(cmd)
    
    stats_filename = dirname + "/sram_stats.csv"

    f = open(stats_filename,'r')
    row = f.readline().strip()
    e = row.split(',')
    sram_cycles = e[0].strip()
    util = e[1].strip()
    f.close()

    return sram_cycles, util

def get_dram_trace(dirname, dest_dir, cat="ifmap"):
    #Return a DRAM trace from the database to the run area

    if cat=='ifmap':
        cmd = "ln -s " + dirname + '/*_ifmap_read.csv ' + dest_dir + "/"
    elif cat=='filter':
        cmd = "ln -s " + dirname + '/*_filter_read.csv ' + dest_dir + "/"
    elif cat=='ofmap':
        cmd = "ln -s " + dirname + '/*_ofmap_write.csv ' + dest_dir + "/"

    os.system(cmd)
    return

def get_log_entries(dirname, dest_dir):
    #Return detailed log entries
    logfilename = dirname + "/dram_stats.csv"

    f = open(logfilename, 'r')
    bw = f.readline().strip()
    #print("BW " + bw)

    details = f.readline().strip()
    #print("DETAIL " + details)
    #details = e[1].strip()
    f.close()

    return bw, details

def create_sram_entry(tag, lname, curr_dir, cycles, util):
    # Copy the files and add a new line to the master table for SRAM data
    dirname = db_home + 'data/' + tag

    cmd = 'mkdir ' + dirname 
    os.system(cmd)

    cmd = 'cp ' + curr_dir + '/*_' + lname + '_sram*.csv ' + dirname
    os.system(cmd)

    stats_filename = dirname + "/sram_stats.csv"
    
    cmd = "touch " + stats_filename
    os.system(cmd)

    f = open(stats_filename, 'w')
    log = str(cycles) + ", " + str(util) + "\n"
    f.write(log)
    f.close()

    dirfile = db_home + dirfilename
    f = open(dirfile, 'a')
    log = tag + ', ' + dirname + "\n"
    f.write(log)
    f.close()
        
    return

    
def create_dram_entry(tag, lname, curr_dir, cat="ifmap"):
    # Copy DRAM trace and create a new line to the master table for DRAM data
    dirname = db_home + 'data/' + tag

    cmd = 'mkdir ' + dirname 
    os.system(cmd)

    if cat == 'ifmap':
        cmd = 'cp ' + curr_dir + '/*_' + lname + '_dram_ifmap*.csv ' + dirname
        os.system(cmd)
    elif cat == 'filter':
        cmd = 'cp ' + curr_dir + '/*_' + lname + '_dram_filter*.csv ' + dirname
        os.system(cmd)
    elif cat == 'ofmap':
        cmd = 'cp ' + curr_dir + '/*_' + lname + '_dram_ofmap*.csv ' + dirname
        os.system(cmd)

    dirfile = db_home + dirfilename
    f = open(dirfile, 'a')
    log = tag + ', ' + dirname + "\n"
    f.write(log)
    f.close()
    
    return

def create_log_entry(tag, bw, detail):
    # Create logs to store the logs
    dirname = db_home + 'data/' + tag

    cmd = 'mkdir ' + dirname 
    os.system(cmd)
    
    stats_filename = dirname + "/dram_stats.csv"
    cmd = 'touch ' + stats_filename
    os.system(cmd)

    f = open(stats_filename, 'w')
    log = bw + "\n"
    f.write(log)

    log = detail + "\n"
    f.write(log)
    f.close()

    dirfile = db_home + dirfilename
    f = open(dirfile, 'a')
    log = tag + ', ' + dirname + "\n"
    f.write(log)
    f.close()


    return

def to_string(inp):
    #Create well formed string from output of subprocess 
    a = str(inp)
    b = a.split("'")[1]
    c = b.split('\\')[0]

    return c
