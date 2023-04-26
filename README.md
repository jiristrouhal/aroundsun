# AroundSun

A little game for anyone, who wants to try to navigate a vessel through a simple solar system.


## Description
You control a red spaceship, that is able to move among four planets, orbiting a sun. You start orbiting a blue planet, closest to the sun. 

<img src=./assets/start.png width="300">

You can then leave the blue planet's orbit and try to reach its neighbours, using tools like showing the trajectory, you are going to take to your destination.

<img src=./assets/going_to_other_planets.png width="400">

To make the navigation easier, you can switch between a static vessel orientation (indicated by the thin red line) and the automatic turning of the vessel into the direction of its movement, relative to the body having the strongest influence on the vessel. You can also make the camera to follow the orbited planets.

<img src=./assets/navigation_and_tracking.gif width="400">


To make your maneuvering less stressful, you can slow down the time and do the burn more precisely. To avoid long and boring waiting (and possibly need to go into a stasis chamber, if you have one), you can speed up the time.  

<img src=./assets/speeding_up_time.gif width="400">

## Controls  

| Key/mouse button | Function |
|-----|----|
| Mouse wheel | Zoom in/out |
| Up arrow | Accelerate forwards |
| Down arrow | Accelerate backwards |
| Shift + up arrow | Accelerate forwards (**10×** thrust) |
| Shift + down arrow | Accelerate backwards (**10×** thrust) |
| Ctrl + up arrow | Accelerate forwards (**0.1×** thrust) |
| Ctrl + down arrow | Accelerate backwards (**0.1×** thrust) |
| Right arrow | Turn right |
| Left arrow | Turn left |
| L | Automatically orient vessel into flight direction |
| P | Pause/resume |
| , | Slow down time 2×|
| . | Speed up time 2× |
| R | Show/hide trajectory |


## Starting the game
Run the *around_sun.py* via you python interpreter (originally developed with Python 3.10.)

## How to contribute
Some ideas, what to add, are
- more planets, of course;
- moons;
- saving/loading the game;
- missions, e.g. getting from planet to planet using the least amount of fuel (or time?)
- ...

## Licence
You are free to use or modify the code under the [MIT licence](./LICENCE).