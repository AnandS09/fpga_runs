import os


def generate_config(
                    fileloc = "./",
                    runname = "default",
                    arrh = 1,
                    arrw = 1,
                    ifmap_sram  = 512,
                    filter_sram = 512,
                    ofmap_sram  = 256,
                    ifmap_offset = 0,
                    filter_offset = 10000000,
                    ofmap_offset = 20000000,
                    dataflow = 'os',
                    topology = "./topologies/test.csv"
        ):

    config_headers = ["[general]", "[architecture_presets]", "[network_presets]"]

    filename = fileloc + "/scale.cfg"
    outfile = open(filename, 'w')

    line = config_headers[0] + "\n"
    outfile.write(line)

    line = "run_name = \"" + runname + "\"\n"
    outfile.write(line)

    line = "\n" + config_headers[1] + "\n"
    outfile.write(line)

    line = "ArrayHeight:\t" + str(arrh) + "\n" 
    outfile.write(line)

    line = "ArrayWidth:\t" + str(arrw) + "\n" 
    outfile.write(line)

    line = "IfmapSramSz:\t" + str(ifmap_sram) + "\n" 
    outfile.write(line)

    line = "FilterSramSz:\t" + str(filter_sram) + "\n" 
    outfile.write(line)

    line = "OfmapSramSz:\t" + str(ofmap_sram) + "\n" 
    outfile.write(line)

    line = "IfmapOffset:\t" + str(ifmap_offset) + "\n" 
    outfile.write(line)

    line = "FilterOffset:\t" + str(filter_offset) + "\n" 
    outfile.write(line)

    line = "OfmapOffset:\t" + str(ofmap_offset) + "\n" 
    outfile.write(line)

    line = "Dataflow:\t" + dataflow + "\n" 
    outfile.write(line)

    line = "\n" + config_headers[2] + "\n"
    outfile.write(line)

    line = "TopologyCsvLoc:\t\"" + topology + "\"\n"
    outfile.write(line)

    outfile.close()
    

def prepare_dir(
                destpath = "./",
                dirname = "scale",
                scale_path = "../scale_sim/"
                ):

    newdirpath = destpath + "/" + dirname
    command = "mkdir " + newdirpath 
    os.system(command) 

    command = "ln -s " + scale_path + "*.py " + newdirpath + "/." 
    os.system(command)
    
    command = "ln -s " + scale_path + "topologies " + newdirpath + "/." 
    os.system(command)
    
    command = "ln -s " + scale_path + "/clean " + newdirpath + "/." 
    os.system(command)


