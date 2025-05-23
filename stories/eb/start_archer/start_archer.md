

# START ARCHER

Begin by checking the container registration
Should this be done in a different file or not
... to realign myself...

Right now all I need is the data directory to be setup properly
We know scale_t * tickers is the containers needed. Do we need 
multiple data paths for all the different containers? NO!!!.
Hes the vision

"""
- data
- - SCALE_T
- - - live
- - - - logs
- - - - - one_scale_bot_log_with_dates
- - - - - another_scale_bot_log_with_dates
- - - - ticker_data
- - - - performance
- - - paper
- - - - logs
- - - - - one_scale_bot_log_with_dates
- - - - - another_scale_bot_log_with_dates
- - - - ticker_data
- - - - performance
- - - - templates
"""

To get this vision done
On start archer we'll set a constant of scale_t = true so we pretend scale_t is registered to start
with archer
with this we'll call setup data_path for scale_t, both live and paper setup

The behaviour is this 
- Check for each path, if any path doesn't exist we'll fail except for live but live is being set 
to false we'll create it just in case but allow success startup.


