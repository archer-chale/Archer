import os

# Name of the container_type
name = "SCALE_T"
base_scale_t_path = os.path.join("data", name)
trade_type_internals = ["logs", "ticker_data", "performance"]
necessary_dirs = []

for tti in trade_type_internals:
    necessary_dirs.append(os.path.join(base_scale_t_path,"live",tti))
    necessary_dirs.append(os.path.join(base_scale_t_path,"paper",tti))

def setup_dirs(container_name):
    if container_name != name:
        return False
    for dir in necessary_dirs:
        os.makedirs(dir)
    return True
    
    