import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes
from matplotlib.text import Text

import math

plt.style.use('dark_background')


root = tk.Tk()
root.wm_title("Oscilátor")

fig = Figure(figsize=(5, 5), dpi=100)

fuel = 0.0


INITIAL_VESSEL_POSITION = [0,2]
INITIAL_VESSEL_VELOCITY = [-1,0]
INITIAL_VESSEL_DIRECTION = [0.0,1.0]
r = INITIAL_VESSEL_POSITION.copy()
u = INITIAL_VESSEL_VELOCITY.copy()
d = INITIAL_VESSEL_DIRECTION.copy()
u_mag = math.sqrt(u[0]*u[0]+u[1]*u[1])
VESSEL_SCALE = 0.33


sun_position = [0,0]


ax:Axes = fig.add_subplot()
vessel, = ax.plot(*r,'.',color='r')
vessel_vel, = ax.plot([r[0],r[0]+VESSEL_SCALE*d[0]], [r[1],r[1]+VESSEL_SCALE*d[1]],color='r')
sun, = ax.plot(*sun_position,'o',color=(1,1,0))
ax.set_xlim(-3,3)
ax.set_ylim(-3,3)
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)
ax.set_frame_on(False)


canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()

CONSUMED_FUEL_LABEL = "Consumed fuel: "
fuel_printout = tk.Label(root,text=CONSUMED_FUEL_LABEL)


time = 0
dt_ms = 1
dt_s = dt_ms/1000.0
G = 1e-05
MS = 500000
M_PLANET = 10000
thrust = 0.0


A_planet_dist = 2
A_planet_phi_0 = 0
A_planet_ang_vel = math.sqrt(MS*G)/A_planet_dist**2

def get_A_planet_position():
    global A_planet_dist, A_planet_phi_0, A_planet_ang_vel, time
    phi = A_planet_ang_vel*time + A_planet_phi_0
    return [A_planet_dist*math.cos(phi), A_planet_dist*math.sin(phi)]

planet_xy = get_A_planet_position()
INITIAL_PLANET_POSITION = planet_xy
planet, = ax.plot([planet_xy[0]],[planet_xy[1]],'o')


def update_A_planet_position():
    global time, dt_s, planet_xy
    time += dt_s
    planet_xy = get_A_planet_position()
    root.after(dt_ms,update_A_planet_position)


N = 100
d_locked = False
TURNING_LOCKED = "Turning LOCKED"
direction_locked_label = tk.Label(root,text="")

def update_position():
    k = G*MS/(r[0]*r[0] + r[1]*r[1])**1.5
    a = [-k*r[0], -k*r[1]]
    

    dt = dt_s/N
    for _ in range(N):
        r_planet = [r[0] - planet_xy[0], r[1] - planet_xy[1]]
        k = G*M_PLANET /(r_planet[0]*r_planet[0] + r_planet[1]*r_planet[1])**1.5
        a_planet = [-k*r_planet[0], -k*r_planet[1]]

        u[0] += (a[0]+a_planet[0])*dt
        u[1] += (a[1]+a_planet[1])*dt

        global thrust, fuel, fuel_printout, d_locked
        
        if thrust!=0: 
            fuel += 1.0/N
            fuel_printout.config(text=CONSUMED_FUEL_LABEL+f"{fuel:.0f}")
            du = thrust*dt
            u[0] += d[0]*du
            u[1] += d[1]*du

        r[0] += u[0]*dt
        r[1] += u[1]*dt

        u_mag2 = u[0]**2 + u[1]**2
        if d_locked and u_mag2>0:
            u_mag = math.sqrt(u_mag2)
            d[0] = u[0]/u_mag
            d[1] = u[1]/u_mag

    thrust = 0
    root.after(dt_ms, update_position)


def redraw():
    vessel.set_data([r[0]],[r[1]])
    vessel_vel.set_data([r[0],r[0]+VESSEL_SCALE*d[0]], [r[1],r[1]+VESSEL_SCALE*d[1]])
    planet.set_data([planet_xy[0]],[planet_xy[1]])
    canvas.draw()
    root.after(10, redraw)


def lock_d(event):
    global d_locked, direction_locked_label
    d_locked = not d_locked
    if d_locked: direction_locked_label.config(text=TURNING_LOCKED)
    else: direction_locked_label.config(text="")


THRUST_MAG = 50
def thrust_forwards(event):
    global thrust 
    if thrust < 0: thrust = 0
    thrust = THRUST_MAG

def thrust_backwards(event):
    global thrust 
    if thrust > 0: thrust = 0
    thrust = -THRUST_MAG

def thrust_forwards_strong(event):
    global thrust 
    if thrust < 0: thrust = 0
    thrust = THRUST_MAG*5

def thrust_backwards_strong(event):
    global thrust 
    if thrust > 0: thrust = 0
    thrust = -THRUST_MAG*5

D_ANGLE = math.pi/40
COS_D_ANGLE = math.cos(D_ANGLE)
SIN_D_ANGLE = math.sin(D_ANGLE)
def turn_left(event):
    global d
    d_old = d.copy()
    d[0] = COS_D_ANGLE*d_old[0]-SIN_D_ANGLE*d_old[1]
    d[1] = SIN_D_ANGLE*d_old[0]+COS_D_ANGLE*d_old[1]

def turn_right(event):
    global d
    d_old = d.copy()
    d[0] = COS_D_ANGLE*d_old[0]+SIN_D_ANGLE*d_old[1]
    d[1] = -SIN_D_ANGLE*d_old[0]+COS_D_ANGLE*d_old[1]


canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
canvas_widget.bind("<Up>",thrust_forwards)
canvas_widget.bind("<Down>",thrust_backwards)
canvas_widget.bind("<Shift-Up>",thrust_forwards_strong)
canvas_widget.bind("<Shift-Down>",thrust_backwards_strong)

canvas_widget.bind("<Left>",turn_left)
canvas_widget.bind("<Right>",turn_right)

canvas_widget.bind("<l>",lock_d)


def reset_positions():
    global time, u, r
    time = 0
    r = INITIAL_VESSEL_POSITION.copy()
    u = INITIAL_VESSEL_VELOCITY.copy()

reset_button = tk.Button(root, text="Reset", command=reset_positions)
fuel_printout.pack()
direction_locked_label.pack()
reset_button.pack()


update_position()
update_A_planet_position()
redraw()
root.mainloop()