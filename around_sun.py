import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes
from matplotlib.lines import Line2D

import dataclasses
from typing import List, Tuple

import math

plt.style.use('dark_background')


root = tk.Tk()
root.wm_title("Around Sun")

fig = Figure(figsize=(7,7))

fuel = 0.0


INITIAL_VESSEL_POSITION = [1.95,0]
INITIAL_VESSEL_VELOCITY = [0,2.5]
INITIAL_VESSEL_DIRECTION = [0.0, 1]
r = INITIAL_VESSEL_POSITION.copy()
u = INITIAL_VESSEL_VELOCITY.copy()
d = INITIAL_VESSEL_DIRECTION.copy()
u_mag = math.sqrt(u[0]*u[0]+u[1]*u[1])
VESSEL_SCALE = 0.33


sun_position = [0,0]

xl = -3.0
xh = 3.0
yl = -3.0
yh = 3.0
k = 0


time = 0
dt_ms = 1
G = 1e-05
MS = 500000
G_MS = G*MS
thrust = 0.0

DT_S_0 = dt_ms/1000.0
dt_s = DT_S_0


def marker_size(size:float)->float:
    return max(size, 0.5)


ax:Axes = fig.add_subplot()
vessel, = ax.plot(*r,'.',color='r')
vessel_vel, = ax.plot([r[0],r[0]+VESSEL_SCALE*d[0]], [r[1],r[1]+VESSEL_SCALE*d[1]],color='r')
THRUST_MAG = 50
STRONG_THRUST_MAG = 10*THRUST_MAG
WEAK_THRUST_MAG = 0.1*THRUST_MAG


trajectory:List[List[float]] = [[], []]
trajectory_image, = ax.plot(*trajectory, '-', color="grey", linewidth=0.5)


sun, = ax.plot(*sun_position,'o',color=(1,1,0),markersize=marker_size(MS/50000))
ax.set_xlim(xl, xh)
ax.set_ylim(yl, yh)
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)
ax.set_aspect('equal')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()

CONSUMED_FUEL_LABEL = "Consumed fuel: "
fuel_printout = tk.Label(root,text=CONSUMED_FUEL_LABEL)


@dataclasses.dataclass
class Planet:
    dist:float
    phi_0:float
    mass:float
    color:str

    def __post_init__(self)->None:
        self.ang_velocity = math.sqrt(MS*G/abs(self.dist)**3)

        self.period = 2*math.pi/self.ang_velocity
        self.n_steps = 2*int(self.period/dt_s)

        self._positions:List[Tuple[float,float]] = list()
        self.__calculate_positions()
        self.period
        self._velocities = [(-self.ang_velocity*ri[1],self.ang_velocity*ri[0]) for ri in self._positions]

        self.init_xy = self.position(0)

    def position(self, time:float)->Tuple[float,float]:
        i = int(time/self.period*self.n_steps)%self.n_steps
        return self._positions[i]
    
    def velocity(self, time:float)->Tuple[float,float]:
        i = int(time/self.period*self.n_steps)%self.n_steps
        return self._velocities[i]
    
    def __calculate_positions(self)->None:
        for k in range(self.n_steps):
            phi = self.phi_0 + k/self.n_steps*2*math.pi
            self._positions.append((self.dist*math.cos(phi), self.dist*math.sin(phi)))
        assert(len(self._positions)==self.n_steps)


planets = [Planet(2,0,5000,'#88F'), Planet(5,-math.pi,1000,'#D60'), Planet(7,-math.pi/2,20000,'#9F3'), Planet(10,-math.pi/2,1000,'#AAA')]


planet_images:List[Line2D] = []
for i in range(len(planets)):
    x,y = planets[i].position(time)
    planet_images.append(*ax.plot([x],[y],'o', markersize=marker_size(planets[i].mass/2500), color=planets[i].color))


d_locked = False
TURNING_LOCKED = "Turning LOCKED"
direction_locked_label = tk.Label(root,text="")


DT0 = DT_S_0
dt = DT0
kt = 0
time_speed_printout = tk.Label(root,text="")


paused = False
def pause(event):
    global paused
    paused = not paused
    set_time_printout()

MAX_SPEEDUP = 7
MAX_SLOWDOWN = 4
def speedup_time(event):
    global kt, dt, paused
    if paused: return 
    if kt<MAX_SPEEDUP: kt += 1
    dt = DT0 * 2**kt 
    set_time_printout()

def slowdown_time(event):
    global kt, dt, paused
    if paused: return 
    if kt>-MAX_SLOWDOWN:
        kt -= 1
    dt = DT0 * 2**kt
    set_time_printout()

def set_time_printout():
    global kt, paused
    message = ""
    if paused:
        message = "Game PAUSED"
    elif kt>0: 
        message = f"Time running {2**kt}× FASTER"
    elif kt<0: 
        message = f"Time running {2**(-kt)}× SLOWER"
    time_speed_printout.config(text=message)



def vec_mag2(vec:List[float]|Tuple[float,float])->float:
    return vec[0]*vec[0] + vec[1]*vec[1]


track_planet:bool = False
tracked_planet_id:int = -1


def update_position():

    global time, thrust, fuel, fuel_printout, d_locked, paused

    if paused: 
        root.after(dt_ms, update_position)
        return 
    
    t_scaling_factor = max(1,2**kt)
    dt_scaled = dt/t_scaling_factor

    for _ in range(t_scaling_factor):

        k = G_MS*(r[0]*r[0] + r[1]*r[1])**(-1.5)
        a_sun = [-k*r[0], -k*r[1]]

        du = 0.0
        if thrust!=0: 
            fuel += abs(thrust)/THRUST_MAG*dt_scaled/DT0
            fuel_printout.config(text=CONSUMED_FUEL_LABEL+f"{fuel:.0f}")
            du = thrust*dt_scaled

        smallest_dist_from_planet_squared = -1.0
        closest_planet_id = -1
        for i in range(len(planets)):
            planet_position = planets[i].position(time)
            dist_from_planet_squared = vec_mag2([r[0]-planet_position[0], r[1]-planet_position[1]])
            if dist_from_planet_squared<smallest_dist_from_planet_squared or smallest_dist_from_planet_squared==-1.0:
                closest_planet_id = i
                smallest_dist_from_planet_squared = dist_from_planet_squared

        p_position = planets[closest_planet_id].position(time)
        r_planet = [r[0] - p_position[0], r[1] - p_position[1]]
        k = G*planets[closest_planet_id].mass*smallest_dist_from_planet_squared**(-1.5)
        a = [-k*r_planet[0], -k*r_planet[1]]


        a_sun_mag2 = vec_mag2(a_sun)
        a_planet_mag2 = vec_mag2(a)

        global tracked_planet_id
        if a_planet_mag2>a_sun_mag2: 
            tracked_planet_id = closest_planet_id
        else:
            tracked_planet_id = -1
        
        u[0] += (a[0] + a_sun[0])*dt_scaled
        u[1] += (a[1] + a_sun[1])*dt_scaled

        if thrust!=0: 
            u[0] += d[0]*du
            u[1] += d[1]*du

        r[0] += u[0]*dt_scaled
        r[1] += u[1]*dt_scaled

        if d_locked:
            if a_planet_mag2>a_sun_mag2: 
                up = planets[closest_planet_id].velocity(time)
                ur = [u[0]-up[0], u[1]-up[1]]
            else:
                ur = u.copy()
            
            ur_mag = math.sqrt(vec_mag2(ur))
            if ur_mag>0:
                d[0] = ur[0]/ur_mag
                d[1] = ur[1]/ur_mag

        time += dt_scaled

    thrust = 0
    root.after(dt_ms, update_position)


PREDICTED_PERIOD = 3
DRAW_EVERY_NTH_TRAJECTORY_POINT = 5
trajectory_visible = False

def predict_trajectory():
    global time, r, dt_s, trajectory, trajectory_visible

    trajectory = [[],[]]

    if trajectory_visible:
        tt = time
        dtt = dt_s
        tt_end = time + PREDICTED_PERIOD
        rr = r.copy()
        uu = u.copy()

        j = 0
        while tt<tt_end:
            k = G_MS*(rr[0]*rr[0] + rr[1]*rr[1])**(-1.5)
            a_sun = [-k*rr[0], -k*rr[1]]

            smallest_dist_from_planet_squared = -1.0
            closest_planet_id = -1
            for i in range(len(planets)):
                planet_position = planets[i].position(tt)
                dist_from_planet_squared = vec_mag2([rr[0]-planet_position[0], rr[1]-planet_position[1]])
                if dist_from_planet_squared<smallest_dist_from_planet_squared or smallest_dist_from_planet_squared==-1.0:
                    closest_planet_id = i
                    smallest_dist_from_planet_squared = dist_from_planet_squared

            p_position = planets[closest_planet_id].position(tt)
            r_planet = [rr[0] - p_position[0], rr[1] - p_position[1]]
            k = G*planets[closest_planet_id].mass*smallest_dist_from_planet_squared**(-1.5)
            a = [-k*r_planet[0], -k*r_planet[1]]

            tt += dtt
            j += 1

            uu[0] += (a[0] + a_sun[0])*dtt
            uu[1] += (a[1] + a_sun[1])*dtt

            rr[0] += uu[0]*dtt
            rr[1] += uu[1]*dtt

            if j%DRAW_EVERY_NTH_TRAJECTORY_POINT==0:
                trajectory[0].append(rr[0])
                trajectory[1].append(rr[1])

    trajectory_image.set_data(*trajectory)

    root.after(250, predict_trajectory)


def redraw():
    global time

    vessel.set_data([r[0]],[r[1]])
    vessel_vel.set_data([r[0],r[0]+VESSEL_SCALE*d[0]], [r[1],r[1]+VESSEL_SCALE*d[1]])
    
    for i in range(len(planets)):
        x,y = planets[i].position(time)
        planet_images[i].set_data([x],[y])

    canvas.draw()
    root.after(dt_ms, redraw)


def lock_d(event):
    global d_locked, direction_locked_label
    d_locked = not d_locked
    if d_locked: direction_locked_label.config(text=TURNING_LOCKED)
    else: direction_locked_label.config(text="")


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
    thrust = STRONG_THRUST_MAG

def thrust_backwards_strong(event):
    global thrust 
    if thrust > 0: thrust = 0
    thrust = -STRONG_THRUST_MAG

def thrust_forwards_weak(event):
    global thrust 
    if thrust < 0: thrust = 0
    thrust = WEAK_THRUST_MAG

def thrust_backwards_weak(event):
    global thrust 
    if thrust > 0: thrust = 0
    thrust = -WEAK_THRUST_MAG

D_ANGLE = math.pi/40
COS_D_ANGLE = math.cos(D_ANGLE)
SIN_D_ANGLE = math.sin(D_ANGLE)

def turn_left(event):
    global d
    dx, dy = d[0], d[1]
    d[0] = COS_D_ANGLE*dx-SIN_D_ANGLE*dy
    d[1] = SIN_D_ANGLE*dx+COS_D_ANGLE*dy

def turn_right(event):
    global d
    dx, dy = d[0], d[1]
    d[0] = COS_D_ANGLE*dx+SIN_D_ANGLE*dy
    d[1] = -SIN_D_ANGLE*dx+COS_D_ANGLE*dy


SINGLE_SCALING = 0.8
k_scaling = 0
def zoom(event:tk.Event):
    global xl, xh, yl, yh, k_scaling

    h = yh-yl
    xc = (xh+xl)*0.5
    yc = (yh+yl)*0.5

    xp = (event.x/event.widget.winfo_width()-0.5)*h + xc
    yp = (0.5-event.y/event.widget.winfo_height())*h + yc

    a = 1.0
    if event.delta>0: 
        #zooming out
        a = SINGLE_SCALING
        k_scaling -= 1
    elif event.delta<0: 
        #zooming in
        a = 1/SINGLE_SCALING
        k_scaling += 1

    s = SINGLE_SCALING**k_scaling
    for i in range(len(planet_images)): 
        planet_images[i].set_markersize(marker_size(planets[i].mass/2500 * s))
    sun.set_markersize(marker_size(MS/50000 * s))

    xl0, xh0, yl0, yh0 = xl, xh, yl, yh

    xl = xp-a*(xp-xl0)
    yl = yp-a*(yp-yl0)
    xh = a*(xh0-xl0) + xl
    yh = a*(yh0-yl0) + yl

    ax.set_xlim(xl,xh)
    ax.set_ylim(yl,yh)


def show_trajectory(event:tk.Event)->None:
    global trajectory_visible
    trajectory_visible = not trajectory_visible


def enable_tracking(event:tk.Event)->None:
    global track_planet
    track_planet = not track_planet


def track():
    global track_planet, tracked_planet_id
    global xl, xh, yl, yh, ax, paused

    if not paused and track_planet==True and tracked_planet_id!=-1:
        prev_position = planets[tracked_planet_id].position(time)
        new_position = planets[tracked_planet_id].position(time-dt)
        dr = [new_position[0]-prev_position[0], new_position[1]-prev_position[1]]

        xl -= dr[0]
        xh -= dr[0]
        yl -= dr[1]
        yh -= dr[1]

        ax.set_xlim(xl,xh)
        ax.set_ylim(yl,yh)

    root.after(dt_ms, track)


canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
canvas_widget.bind("<Up>",thrust_forwards)
canvas_widget.bind("<Down>",thrust_backwards)
canvas_widget.bind("<Shift-Up>",thrust_forwards_strong)
canvas_widget.bind("<Shift-Down>",thrust_backwards_strong)
canvas_widget.bind("<Control-Up>",thrust_forwards_weak)
canvas_widget.bind("<Control-Down>",thrust_backwards_weak)
canvas_widget.bind("<Left>",turn_left)
canvas_widget.bind("<Right>",turn_right)

canvas_widget.bind("<MouseWheel>",zoom)

canvas_widget.bind("<l>",lock_d)

canvas_widget.bind("<p>",pause)
canvas_widget.bind("<t>", enable_tracking)
canvas_widget.bind("<.>", speedup_time)
canvas_widget.bind("<,>", slowdown_time)

canvas_widget.bind("<r>", show_trajectory)



def reset():
    global time, u, r, fuel
    fuel = 0.0
    time = 0
    r = INITIAL_VESSEL_POSITION.copy()
    u = INITIAL_VESSEL_VELOCITY.copy()

reset_button = tk.Button(root, text="Reset", command=reset)
fuel_printout.pack()
direction_locked_label.pack()
time_speed_printout.pack()
reset_button.pack()


update_position()
redraw()
track()
predict_trajectory()


def main():
    global root
    root.mainloop()


if __name__=="__main__":
    main()

