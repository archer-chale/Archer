


confirm

disable it to confirm everything else works,

Find a different stock to experiment with
-> Note, later own we can account for the external shares using the SPC

Nahh we are not finding different stock for limiting spread out list

We'll stick to soxl and use this opportunity to implement auto shift up

Tasks
1. Ensure we add leftover cash to last index of csv file so no money is left untouched *
2. Shifting/ Adding new line above csvs process
-> a function that takes a current price
-> Strategy is overlaying the new line with previous index 0
-> Illustration bp, 20.00, 19.99 <--> sp, 20.50, 20.49
-> we'll go with this strategy until something break, else we'll so gap expand kind of strategy
-> Moving on
-> when function is called, we assume all checks have been handled(no shares currently held on both sides)
-> once an insertion is done
-> we balance the cash again( calling linear distribute again - Perhaps we extract this function out)
-> each call, we check the half percentage gap to see if we can expand gap/ shift till perfect overlay
-> if not insert new overlay
3. Once shifting is implemented, see if we can unit test this
4. Whatever happens on unit testing, we test this with SOXL so we have live tested it
5. Implement the use case through csv_service so it auto does it as needed
6. Live test it, we don't need to get to actual buys but just shifting
7. After live tested and we've seen expected behaviour we then 
8. Ensure SPC honoring is active if not implement
9. Use SPC disactivation honor to insert RobinT's shares so share checks are fine
10. Live test this.
11. Make necessary CR's
12. Anything else needed to fully migrate SOXL?