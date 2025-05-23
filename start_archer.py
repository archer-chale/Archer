from main.bots.SCALE_T.setup_dirs import name as scale_t_name, setup_dirs as scale_t_setup

"""
Graduation steps
Currently i'll have generate compose call this file's main to create necessary files.
This main will end up creating the necessary file paths needed. for each registered bothss
Right now, to ensure paths are setup properly

GOALL
This is a goal file
I Have the goal that this file will create 
1. All the folders and files necessary to run archer and associated bots
    - complicated orchestration but necessary
2. Build new images of all necessary bots and containers
4. Spin up some archer container - don't even know what its for
3. Spin up all registered containers

"""

def main():
    print("Starting Archer")
    # Will need some configuration for each container so we can setup paths and files as needed
    # Assume this list came from the configuration
    containers = [ 'SCALE_T' ]
    for container in containers:
        if container == scale_t_name:
            scale_t_setup(container)
            print(f"Setup done for {container}")
    return 
    

# Graduation step no. 1
if __name__ == "__main__":
    main()
