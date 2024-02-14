import numpy as np

def ck_tb_mem ( logger, args ):
	mu = int(args['units'])
	mem_depth = int(args['size'])
	for i in range(mu):
		fi = open(f"input_file_{i}.txt", "r")
		fr = open(f"result_file_{i}.txt", "r")
		for j in range(mem_depth):
			g_sample = int(fi.readline())
			sample = int(fr.readline())
			if (g_sample != sample):
				logger.error(f"Master-Salve[{str(mu)}] - Line {str(j)}: Reference {str(g_sample)} does not match result {str(sample)}")
				return 1
	return 0

def ck_tb_mem_shared ( logger, args ):
  mu = int(args['units'])
  mem_depth = int(int(args['size'])/2)
  for i in range(mu):
    fi = open(f"input_file_{i}.txt", "r")
    fr = open(f"result_file_{i}.txt", "r")
    for j in range(mem_depth):
      g_sample = int(fi.readline())
      sample = int(fr.readline())
      if (g_sample != sample):
        logger.error(f"Master-Salve[{str(mu)}] - Line {str(j)}: Reference {str(g_sample)} does not match result {str(sample)}")
        return 1
  return 0

def ck_tb_mem_busy ( logger, args ):
  mu = int(args['units'])
  mem_depth = int(int(args['size'])/mu)
  for i in range(mu):
    fi = open(f"input_file_{i}.txt", "r")
    fr = open(f"result_file_{i}.txt", "r")
    for j in range(mem_depth):
      g_sample = int(fi.readline())
      sample = int(fr.readline())
      if (g_sample != sample):
        logger.error(f"Master-Salve[{str(mu)}] - Line {str(j)}: Reference {str(g_sample)} does not match result {str(sample)}")
        return 1
  return 0

