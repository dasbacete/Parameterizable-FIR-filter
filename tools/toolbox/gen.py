import numpy as np

def gen_tb_mem ( args ):
  mu = int(args['units'])
  mem_depth = int(args['size'])
  for i in range(mu):
    fd = open(f"input_file_{i}.txt", "w")
    content = np.random.randint(-1000,1000,size=mem_depth)
    for n in content:
      fd.write(f"{n}\n")
    fd.close()

def gen_tb_mem_shared ( args ):
  mu = int(args['units'])
  mem_depth = int(int(args['size'])/2)
  for i in range(mu):
    fd = open(f"input_file_{i}.txt", "w")
    content = np.random.randint(-1000,1000,size=mem_depth)
    for n in content:
      fd.write(f"{n}\n")
    fd.close()

def gen_tb_mem_busy ( args ):
  mu = int(args['units'])
  mem_depth = int(int(args['size'])/mu)
  for i in range(mu):
    fd = open(f"input_file_{i}.txt", "w")
    content = np.random.randint(-1000,1000,size=mem_depth)
    for n in content:
      fd.write(f"{n}\n")
    fd.close()
