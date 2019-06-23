import os

df_list = ['ws', 'is']

cmd = "mkdir scale_runs_out"
os.system(cmd)

for i in range(1,11):
    num_proc = 96 * 1

    for df in df_list: 
        target_name = "./scale_runs/9x" + str(num_proc) + "_" + df + "/outputs/"
        
        dest = '9x' + str(num_proc) + "_" + df 
        cmd = 'mkdir ' + dest 
        os.system(cmd)

        cmd = "cp -r " + target_name + " " + dest + "/"
        os.system(cmd)

        cmd = "mv " + dest + " scale_runs_out/"
