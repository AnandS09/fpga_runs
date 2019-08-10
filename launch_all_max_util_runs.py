import utilities as ut
import os
import math
import multiprocessing as mp
import subprocess as sp

scale_path = "/home/anand/repos/fccm_scale_runs/silent_scale_sim/"
num_phy_proc = 960                  # Number of physical processors available on chip
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

    # This is to account for the increase in number of cols 
    # without the increase in total memory of the device
    simd_mode = True
    factor = 1
    if simd_mode:
        factor = 2

    #cmd = "mkdir ./scale_runs/"
    #os.system(cmd)
    
    # Set the step size of the processors
    step_size = 0.1     # This is the step size in fraction of total number of processors
    proc_per_step = math.ceil(step_size * num_phy_proc)

    # Scale the memory per processor
    rescale_params(factor=factor)
    
    # Set the iterable lists
    topo_list_this = topo_list[0:-2]
    mult_list = [x  for x in range(1,11)]

    for topo in topo_list_this:
        jobs = []

        for i in mult_list:
            num_rows = 9
            num_cols = int(math.ceil(proc_per_step * i))
            
            for df_idx in range(2):
                df = df_list[df_idx]
                weight_mem = int(weight_mem_per_proc[df_idx] * num_cols / 8)  # div 8 converts to KB
                input_mem = int(input_mem_per_proc[df_idx] * num_cols / 8)
                output_mem = int(output_mem_per_proc[df_idx] * num_cols / 8)   

                destpath = "./scale_runs"
                dirname = str(num_rows) + "x" + str(num_cols) + "_" + df 
                runname = topo.split('.')[0] + "_" + dirname

                if first:
                    ut.prepare_dir(
                            destpath = destpath,
                            dirname=dirname,
                            scale_path=scale_path
                            )

                topo_num_cols = num_cols 
                fileloc = destpath +"/"+dirname    
                topology  = "/home/anand/repos/fccm_scale_runs/max_util_topo/" 
                #topology += df + "/max_util_" + df + "_" + str(topo_num_cols) + "/" + topo
                topology += df + "/" + topo
                topology += "_" + df + "_" + str(topo_num_cols) + ".csv"
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

                job = mp.Process(target=scale_run,args=(num_rows,num_cols,df_idx, weight_mem, input_mem))
                jobs.append(job)
            
        first = False
        
        num_jobs = len(jobs)
        fraction = 0.5
        batch_size = int(fraction * num_jobs)
        start_idx = 0
        remaining = num_jobs

        while remaining > 0:
            runs_this_iter = min(remaining, batch_size)
            end_idx = start_idx + runs_this_iter

            for job in jobs[start_idx: end_idx]:
                job.start()

            msg = "Started jobs "+str(start_idx)+" to " +str(end_idx)+" for " + topo
            print(msg, end="")

            for job in jobs[start_idx: end_idx]:
                job.join()
            print(": Done")
        
            remaining -= runs_this_iter
            start_idx += runs_this_iter

        print("All jobs for " + topo + " finished")
       

launch_runs()
