

Hi, wasn't gonna create this file and plan this outside but i figured it'll help me and pr reviewer so
:)

So lets see, the goal of this.

So right now we run things in the background with paper assumed as a background task.

Lets think of the startup process. We have to generate the docker-compose and then run the bots manually
I think this process is cumbersome. Easy to start should me the mantra. Obviously we need a config file 
or two to ensure information is available to run "easy". Will tackle as needed. 

Main components needed to go live is

- Allow the live diversity
- - Add live config in config files ( more a readme task )
- - generate compose shouldn't use 'paper' constant to launch bots
- - using of live config by all bots when specified, properly
- CSV problem
* Currently you could do live with the current csv generation tool but its not optimized for logical, user
desired price ladder and automatic optimizations.?
- - The creation and management of csvs are very related.?
- - Picking stock and having it deregulated by management?

- startup optimizations
- - look into using docker-py in place of generate compose and optimization
- - a higher level startup script(python/shell) command to 

### Add live config in config files ( more a readme task )

