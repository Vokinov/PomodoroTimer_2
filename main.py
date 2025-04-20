import tkinter as tk
import tkinter.font as tkFont
from pathlib import Path
from pygame import mixer
from math import sin, cos, radians
import platform

# Sarting pygame mixer
mixer.init()
    

# Global variables

# Paths definitions
script_dir = Path(__file__).resolve().parent # The absolute path of the current script
assets_dir = script_dir / "assets"
images_dir = assets_dir / "images"
sounds_dir = assets_dir / "sounds"
#Font definition
font="Arial"
font_color = '#12FF15'
background_img = images_dir / "background.png"
background_color = 'black'
counter_seconds = 1500  # Starting time setting of timer().
work_passed = 0  # Counts seconds of work time passed.
break_passed = 0  # Counts seconds of breaks passed.
flow = 0  # 0 means no timer function instance is running.
work_check = True  # Checks if timer runs with work (default) or break time.
radius = 68  # Length of Progress Gauge pointer.
# Variables needed to access them from main() outer level and pointer_update() inner level.
circle = None
pointer = None

# List of sound names and files.
alarm_sound_files = {
    'Breaking Glass': sounds_dir / 'breaking_glass.mp3',
    'Calm String': sounds_dir / 'calm_string.mp3',
    'Dramatic Riser': sounds_dir / 'dramatic_riser.mp3',
    'Epic Intro': sounds_dir / 'epic_intro.mp3',
    'Flute': sounds_dir / 'flute.mp3',
    'Game Alarm': sounds_dir / 'game_alarm.mp3',
    'Reggae Loop': sounds_dir / 'reggae_loop.mp3',
    'Sfx Glitch': sounds_dir / 'sfx_glitch.mp3',
    'Shotgun': sounds_dir / 'shotgun.mp3',
    'Wtf Alert': sounds_dir / 'wtf_alert.mp3'
}

# Text for About frame.
about = '''This app facilitates the use of Pomodoro time management technique. It helps keep focus and balance between work and \
rest.Work and Break buttons reset timer with adjusted time settings. Also they stop sound playback while it is running. Progress Gauge and Goal Completion updates every minute. Sound test is possible only when Timer is not running.'''


def main():
    # Starting tkinter, settings for main window.
    root = tk.Tk()
    root.resizable(False, False)
    root.title('Pomodoro Timer')
    root.geometry('600x600+300+300')

    
    # Set window icon cross-platform
    icon_base = images_dir / "icon"
    try:
        if platform.system() == "Windows":
            root.iconbitmap(f"{icon_base}.ico") # Windows supports .ico file type for icons
        else:
            icon_img = tk.PhotoImage(file=f"{icon_base}.png") # Linux and MAC supports .png file type
            root.iconphoto(True, icon_img)
    except Exception as e:
        print(f"Icon loading failed: {e}")

    # Setting main window background.
    bg = tk.PhotoImage(file=background_img)  # image size 600x600
    canvas = tk.Canvas(root, borderwidth=0)
    canvas.pack(fill='both', expand=True)
    canvas.create_image(0, 0, image=bg, anchor='nw')
    canvas.create_text(300, 43, text='POMODORO TIMER', font=(font, 40, 'bold'), fill=background_color)

    def goal_update():
            try:
                goal_seconds = hours_input.get() * 3600 + minutes_input.get() * 60
                if goal_seconds == 0:
                    progress_label.config(text="No goal set")
                    return
                global session_goal_seconds
                session_goal_seconds = goal_seconds  # Store updated goal
                progress_percent = (work_passed / goal_seconds) * 100
                progress_percent = min(progress_percent, 100)  # Cap at 100%
                progress_label.config(text=f"Goal Progress:   {progress_percent:.1f}%")
            except Exception as e:
                progress_label.config(text="Invalid input")
                print(f"Goal update error: {e}")

    # Creating Session Work Time frame with two spinboxes for user input.
    # Hours spinbox
    hours_input = tk. IntVar()
    hours_input.set(0)
    goal_frame = tk.LabelFrame(root, fg=font_color, bg=background_color)
    canvas.create_window(300, 440, height=40, width=240, anchor='n', window=goal_frame)
    canvas.create_text(300, 420, text='Session work time goal', font=(font, 16, 'bold'), fill=font_color)
    hours_spin = tk.Spinbox(goal_frame, textvariable=hours_input, font=(font, 12, 'bold'), width=2, from_=0, to=12,
                            bg=background_color, fg=font_color, validate='all', wrap=True, command=goal_update)
    hours_spin.grid(column=1, row=1, padx=6, pady=6)
    hours_label = tk.Label(goal_frame, fg=font_color, bg=background_color, font=(font, 12, 'bold'), text='hours ')
    hours_label.grid(column=2, row=1, padx=0, pady=6)

    # Minutes spinbox
    minutes_input = tk.IntVar()
    minutes_input.set(25)
    minutes_spin = tk.Spinbox(goal_frame, textvariable=minutes_input, font=(font, 12, 'bold'), width=2, from_=0, to=60,
                              bg=background_color, fg=font_color, validate='all', wrap=True, command=goal_update)
    minutes_spin.grid(column=3, row=1, padx=0, pady=6)
    minutes_label = tk.Label(goal_frame, fg=font_color, bg=background_color, font=(font, 12, 'bold'), text='  minutes')
    minutes_label.grid(column=4, row=1, padx=0, pady=6)

    # Drawing colourful arc for Progress Gauge.
    for arc_degree in range(0, 181):
        canvas.create_arc(425, 160, 565, 300, start=arc_degree, extent=2, outline=arc_color_update(arc_degree), width=15,
                          style=tk.ARC)

    # Creating Progress Gauge text and pointer.
    canvas.create_text(500, 130, text='Progress Gauge', font=(font, 16, 'bold'), fill=font_color)
    global circle
    circle = canvas.create_oval(488, 223, 502, 237, fill='red')
    global pointer
    pointer = canvas.create_line(495, 230, (495 - radius * cos(0)), (230 - radius * sin(0)), width=3, arrow='last',
                                 arrowshape=(radius, radius, 4), fill='red')

    # Creating Goal Completion Frame.
    progress_frame = tk.LabelFrame(root, fg=font_color, bg=background_color)
    canvas.create_window(495, 250, height=55, width=150, anchor='n', window=progress_frame)
    progress_label = tk.Label(progress_frame, fg=font_color, bg=background_color, font=(font, 12, 'bold'),
                              text='Goal Progress    0.0%', wraplength=160)
    progress_label.pack(padx=3, pady=3)


    # Updates pointer of Progress Gauge. Called from timer().
    def pointer_update():
        global pointer
        global circle
        canvas.delete(pointer, circle)
        goal_minutes = hours_input.get() * 60 + minutes_input.get()
        in_radian = 1.8 * radians(completion(work_passed, goal_minutes))  # scale value in radian
        circle = canvas.create_oval(488, 223, 502, 237, fill=arc_color_update(
                180-round(completion(work_passed, goal_minutes)*1.8)))
        pointer = canvas.create_line(495, 230, (495 - radius * cos(in_radian)), (230 - radius * sin(in_radian)), width=6,
                                     arrow='last', arrowshape=(radius, radius, 3),
                                     fill=arc_color_update(180-round(completion(work_passed, goal_minutes)*1.8)))

    

    # Updates sound volume
    def volume_update(val):
        if mixer.get_init() and mixer.music.get_busy():
            mixer.music.set_volume(int(val) / 100)

    #  Menu for choosing sound.
    sound_click = tk.StringVar()
    sound_click.set('Calm String')
    sound_menu = tk.OptionMenu(root, sound_click, *alarm_sound_files.keys())
    canvas.create_window(30, 150, height=40, width=150, anchor='nw', window=sound_menu)
    sound_menu.config(width=12, font=(font, 12, 'bold'), bg=background_color, fg=font_color, borderwidth=5,
                      activebackground=background_color, activeforeground=font_color, highlightthickness=0)
    sound_menu['menu'].config(borderwidth=0, font=(font, 12, 'bold'), bg=background_color, fg=font_color,
                              activebackground='black', activeforeground=font_color, bd=5, relief='raised')
    sound_menu['borderwidth'] = 3
    canvas.create_text(100, 130, text='Sound Menu', font=(font, 16, 'bold'), fill=font_color)

    # Slider for setting volume.
    volume_value = tk.IntVar()
    volume_value.set(100)
    # Updating sound volume while playing sound
    volume_slider = tk.Scale(root, activebackground=background_color, troughcolor=background_color, 
                             bg=background_color, fg=font_color, border=1, highlightthickness=0, 
                             highlightbackground=background_color, font=(font, 12, 'bold'),
                             from_=0, to=100, orient='horizontal', variable=volume_value, command=volume_update) 
    canvas.create_window(50, 350, width=140, height=44, anchor='nw', window=volume_slider)
    canvas.create_text(120, 330, text='Volume', font=(font, 16, 'bold'), fill=font_color)

    # Reads chosen sound file, sets volume, plays sound.
    def play_music():
        mixer.init()
        if mixer.music.get_busy():
            mixer.music.stop()
        else:   
            filename = alarm_sound_files.get(sound_click.get(), sounds_dir / 'calm_string.mp3')
            mixer.music.load(str(filename))
            mixer.music.set_volume(volume_value.get() / 100)
            mixer.music.play()

    # Starts and stops Sound Test if timer() is not busy.
    def sound_test():
        if flow == 0:
            mixer.init()
            if mixer.music.get_busy():
                mixer.music.stop()
            else:
                mixer.init()
                filename = alarm_sound_files.get(sound_click.get(), sounds_dir / 'calm_string.mp3')
                mixer.music.load(filename)
                mixer.music.set_volume(volume_value.get() / 100)
                mixer.music.play()

    # Sound test button
    test_button = tk.Button(root, activebackground=background_color, activeforeground=font_color, height=1, text='Start / Stop',
                            borderwidth=5, font=(font, 12, 'bold'), bg=background_color, fg=font_color, command=sound_test)
    canvas.create_window(34, 250, height=47, width=140, anchor='nw', window=test_button)
    canvas.create_text(100, 230, text='Sound Test', font=(font, 16, 'bold'), fill=font_color)

    # Pauses timer().
    def pause_function():
        global flow
        flow = 0
        start_button.config(state='normal')
        
    # Pause button
    pause_button = tk.Button(root,  activebackground=background_color, activeforeground=font_color, text='Pause', borderwidth=5,
                             height=1, font=(font, 18, 'bold'), bg=background_color, fg=font_color, command=pause_function)
    canvas.create_window(310, 250, height=57, width=90, anchor='nw', window=pause_button)

    # Stops timer(), reads worktime as counter_seconds, sets timer() to count time as a work time.
    def work_function():
        mixer.music.stop()
        global flow
        global work_check
        global counter_seconds
        flow = 0
        counter_seconds = work_minutes.get() * 60
        if counter_seconds == 3600:  # There are only fields for minutes and seconds so one hour is 59m:59secs in this app.
            counter_seconds = 3599
        timer_label['text'] = timer_update(counter_seconds)
        work_check = True

    # Work button
    work_button = tk.Button(root, activebackground=background_color, activeforeground=font_color, text='Work', borderwidth=5,
                            font=(font, 18, 'bold'), bg=background_color, fg=font_color, command=work_function)
    canvas.create_window(200, 80, height=57, width=90, anchor='nw', window=work_button)

    # Slider for setting duration (in minutes) of a worktime.
    work_minutes = tk.IntVar()
    work_minutes.set(25)
    work_slider = tk.Scale(root, activebackground=background_color, troughcolor=background_color,  bg=background_color,
                           fg=font_color, border=1, highlightthickness=0, highlightbackground=background_color,
                           font=(font, 12, 'bold'), from_=15, to=60, orient='horizontal', variable=work_minutes)
    canvas.create_window(230, 350, width=140, height=44, anchor='nw', window=work_slider)
    canvas.create_text(300, 330, text='Work time', font=(font, 16, 'bold'), fill=font_color)

    # Slider for setting duration (in minutes) of a break.
    break_minutes = tk.IntVar()
    break_minutes.set(5)
    break_slider = tk.Scale(root, activebackground=background_color, troughcolor=background_color, bg=background_color,
                            fg=font_color, border=1, highlightthickness=0, highlightbackground=background_color,
                            font=(font, 12, 'bold'), from_=5, to=30, orient='horizontal', variable=break_minutes)
    canvas.create_window(410, 350, width=140, height=44, anchor='nw', window=break_slider)
    canvas.create_text(480, 330, text='Break time', font=(font, 16, 'bold'), fill=font_color)

    # Creating Timer label.
    timer_label = tk.Label(root, width=6, height=1, text=str(work_minutes.get()) + ':00', relief='raised', borderwidth=5,
                           font=(font, 40, 'bold'), bg=background_color, fg=font_color)
    canvas.create_window(200, 150, width=200, anchor='nw', window=timer_label)

    # About frame
    about_frame = tk.LabelFrame(root, labelanchor='n', font=('Calibri', 10, 'bold'), foreground=font_color, text='About',
                                bg=background_color)
    canvas.create_window(300, 485, height=110, width=580, anchor='n', window=about_frame)
    about_label = tk.Label(about_frame, text=about, justify='left', wraplength=574, borderwidth=0, font=('Calibri', 10,),
                           bg=background_color, fg=font_color)
    about_label.place(relx=.5, rely=.55, anchor='center', bordermode='outside')


    # Starts timer(). Allows only one instance of timer() running.
    def start_function():
        global flow, counter_seconds
        if not mixer.music.get_busy() and counter_seconds > 0:
            flow += 1
            if flow == 1:
                start_button.config(state='disabled')  # Disable during countdown
                timer()


    # Start button
    start_button = tk.Button(root, activebackground=background_color, activeforeground=font_color, height=1, text='Start',
                             borderwidth=5, font=(font, 18, 'bold'), bg=background_color, fg=font_color,
                             command=start_function)
    canvas.create_window(200, 250, height=57, width=90, anchor='nw', window=start_button)


    # Counts down seconds, updates time label every second. Counts seconds of worktime and breaks passed.
    # Triggers timer_update(), goal_update() and play_music().
    def timer():
        global flow
        mixer.init()
        if not mixer.music.get_busy() and flow > 0:
            global work_passed
            global break_passed
            global counter_seconds
            if counter_seconds >= 0:
                timer_label['text'] = timer_update(counter_seconds)
                counter_seconds -= 1
                if work_check:
                    work_passed += 1
                else:
                    break_passed += 1
                if work_passed % 10 == 0:  # Updating Progress Gauge and Goal Completion every ten seconds.
                    goal_update()
                    pointer_update()
                root.after(985, timer)  # 15 milliseconds subtracted for timer() operation time.
            else:  # If timer reaches 0 it plays sound and resets its instance counter.
                flow = 0
                play_music()
                start_button.config(state='normal')


    # Stops timer(), sets timer() to count time as a break.
    def break_function():
        mixer.music.stop()
        global counter_seconds
        global work_check
        global flow
        flow = 0
        counter_seconds = break_minutes.get() * 60
        timer_label['text'] = timer_update(counter_seconds)
        work_check = False

    # Break button
    break_button = tk.Button(root, activebackground=background_color, activeforeground=font_color, text='Break',
                             borderwidth=5, font=(font, 18, 'bold'), background=background_color, fg=font_color,
                             command=break_function)
    canvas.create_window(310, 80, height=57, width=90, anchor='nw', window=break_button)

    # Closing mixer on app close
    def on_closing():
        if mixer.get_init():
            mixer.quit()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
        
    # Starting app window
    root.mainloop()


# Creating Progress Gauge text and drawing.
def arc_color_update(degree):
    change = int((255/180)*degree)  # Jump in colour value for each degree of arc angle.
    color_c = f'#{change:02x}{255-change:02x}00'
    return color_c


# Calculates the percentage of goal completion
def completion(work_seconds, goal_minutes):
    goal_seconds = goal_minutes * 60
    if goal_seconds == 0:
        return 0
    return min(100, (work_seconds / goal_seconds) * 100)

# It's used to read counter_seconds global value and update Timer label.
def timer_update(counter_seconds):
    minutes, seconds = divmod(counter_seconds, 60)
    return f'{minutes:02d}:{seconds:02d}'

if __name__ == "__main__":
    main()
