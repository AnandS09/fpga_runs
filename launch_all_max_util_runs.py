import utilities as ut
import os
import math
import multiprocessing as mp
import subprocess as sp

scale_path = "/home/anand/repos/fccm_scale_runs/silent_scale_sim/"
simd_mode = 1
num_proc = 96 
weight_mem_per_proc= [36, 288]      # Conv: 36 kbit, Mat Mul: 288 kbit 
input_mem_per_proc= [252,162]       # Conv: 288 - 36 kbit, Mat Mul:18 * 9 kbit
output_mem_per_proc = [288, 18]     # Conv: One URAM, Mat Mul: one BRAM

df_list = ['ws', 'is']
#df_list = ['ws']

topo_list = [
                "FasterRCNN",
                "DeepSpeech2",
                "AlphaGoZero",
                "NCF_recommendation",
                "Resnet50",
                "Sentimental_seqCNN",
                "Googlenet",
                "vgg16",
                "alexnet" 
            ]

#topo_list = ["alexnet.csv"]

def scale_run(arrh=1, arrw=1, df_idx = 0, weight_mem=1, input_mem=1):
    #scale_run_path = "./scale_runs/" + str(weight_mem) + "KB_WeightMem_" + str(input_mem) + "KB_IfmapMem_"
    #scale_run_path += str(arrh) + "x" + str(arrw) + "_" + str(df_list[df_idx])
    scale_run_path = "./scale_runs/" + str(arrh) + "x" + str(arrw) + "_" + str(df_list[df_idx])
    command = ["python", "scale.py"]
    p = sp.Popen(command, cwd=scale_run_path)
    p.wait()

def rescale_params(factor=10):
    global weight_mem_per_proc
    global input_mem_per_proc
    global output_mem_per_proc

    weight_mem_per_proc[0] = math.ceil(weight_mem_per_proc[0]/factor)
    weight_mem_per_proc[1] = math.ceil(weight_mem_per_proc[1]/factor)

    input_mem_per_proc[0] = math.ceil(input_mem_per_proc[0]/factor)
    input_mem_per_proc[1] = math.ceil(input_mem_per_proc[1]/factor)

    output_mem_per_proc[0] = math.ceil(output_mem_per_proc[0]/factor)
    output_mem_per_proc[1] = math.ceil(output_mem_per_proc[1]/factor)


def launch_runs():
    jobs = []
    #first = False 
    first = True
    factor = 1
    #cmd = "mkdir ./scale_runs/"
    #os.system(cmd)
    
    #topo_list_this = [topo_list[5], topo_list[7]]
    #topo_list_this = [topo_list[2]]
    topo_list_this = topo_list[0:-1]

    rescale_params(factor=factor)
    
    mult_list = [x  for x in range(1,11)]
    #mult_list += [20, 50]
    #mult_list = [10]
    #mem_mult_list = [x for x in range (1,11)]
    #mem_mult_list += [0.5, 0.2]

    for topo in topo_list_this:
        jobs = []

        #for i in range(1,11):
        for i in mult_list:
        #for i in mem_mult_list:
            num_rows = 9
            num_cols = int(math.ceil(num_proc/factor * i))
            #num_cols = int(num_proc * 10)
            
            for df_idx in range(2):
                df = df_list[df_idx]
                weight_mem = int(weight_mem_per_proc[df_idx] * num_cols / 8)  # div 8 converts to KB
                #weight_mem = int(weight_mem_per_proc * num_cols / (8 * i))  # div 8 converts to KB
                input_mem = int(input_mem_per_proc[df_idx] * num_cols / 8)
                #input_mem = int(input_mem_per_proc * num_cols / (8 * i))
                output_mem = int(output_mem_per_proc[df_idx] * num_cols / 8)   

                destpath = "./scale_runs"
                #dirname = str(weight_mem) + "KB_WeightMem_" + str(input_mem) + "KB_IfmapMem_"
                #dirname += str(num_rows) + "x" + str(num_cols) + "_" + df 
                dirname = str(num_rows) + "x" + str(num_cols) + "_" + df 
                runname = topo.split('.')[0] + "_" + dirname
                #scale_path = "./silent_scale_sim/"

                if first:
                    ut.prepare_dir(
                            destpath = destpath,
                            dirname=dirname,
                            scale_path=scale_path
                            )
                fileloc = destpath +"/"+dirname    
                topology  = "/home/anand/repos/fccm_scale_runs/max_util_topo/" 
                topology += df + "/max_util_" + df + "_" + str(num_cols) + "/" + topo
                topology += "_" + df + "_" + str(num_cols) + ".csv"
                ut.generate_config(
                        fileloc=fileloc,
                        runname=runname,
                        arrh=num_rows,
                        arrw=num_cols,
                        ifmap_sram=input_mem,
                        filter_sram=weight_mem,
                        ofmap_sram=output_mem,
                        dataflow=df,
                        topology=topology
                        )

                #job = mp.Process(target=scale_run,args=(num_rows,num_cols,df_idx))
                job = mp.Process(target=scale_run,args=(num_rows,num_cols,df_idx, weight_mem, input_mem))
                jobs.append(job)
            
        first = False
        for job in jobs:
            job.start()

        print("Started all jobs for " + topo)
        
        for job in jobs:
            job.join()

        print("All jobs for " + topo + " finished")
       

launch_runs()
