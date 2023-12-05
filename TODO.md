# TODO

FIXME cleanup README and TODO


new name petminion (petminion.org registered)

- DONE make proposed state machine for initial crow and cat trainer - figure out how to deal with multiple deliveries for multiple rewards
- make basic API for recognizer/camera
- make state machineish training rules engine (find existing state machine lib?) https://github.com/pytransitions/transitions
- add github actions to do test builds and run tests per https://github.com/geeksville/petminion/actions/new
-   Get remote debugging working
-   Have recognizer save interesting frames to a directory.  Where interesting
    can be: something not blank, something that is a bird.
-   have a blacklist of mistaken matches which we will never consider interesting  
-   Store image and the matching terms in a separate datafile  
-   Only store a max of one frame every 30 seconds.
-   Tweet when we saw something interesting
-   Store a short movie every time we see something interesting (and tweet it as a gif)
-   automatically load training rules from a directory.  This will allow users to make/share rules without using git/github
-   Use a should_trigger() method in the rules to allow multiple rules to be candidates at once
-   Add hotreloading of rules based on file changes
- have the python app auto fetch teh (huge) machine vision model files
- link petminion.org to the github pages site
- 
during development post 'success' images to mastodon https://mastodonpy.readthedocs.io/en/stable/

