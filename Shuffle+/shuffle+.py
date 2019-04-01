import os
import pygame
import sqlite3
import random
from tkinter import *
from tkinter.filedialog import askdirectory
from mutagen.id3 import ID3
from mutagen.mp3 import MP3

conn = sqlite3.connect("musicdata.db")
root = Tk()
root.geometry("606x304")
root.title("Shuffle+")
root.iconbitmap("play_pause___copy_crop_f02_icon.ico")
directory = "c:/"

def get_directory():
    global directory
    directory = askdirectory()
    f = open("directory.bin","w")
    f.write(directory)
    f.close()


try:
    f = open("directory.bin","r")
except IOError:
    get_directory()

f = open("directory.bin", "r")
directory = f.read()
top_frame = Frame(root, bg="white")
top_frame.pack(fill=BOTH, expand=FALSE, side="top")
bottom_frame = Frame(root, bg="white")
bottom_frame.pack(fill=BOTH, expand=FALSE, side="bottom")
temp_directory = os.getcwd()
os.chdir(directory)
i = 0

listsongs = []
artists_names_times = []
time_secs = []
play = True

for files in os.listdir(directory):
    if files.endswith(".mp3"):
        now = ID3(files)
        audio = MP3(files)
        time = audio.info.length
        time_secs.append(time)
        time /= 60
        time = round(time,2)
        if "." in str(time):
            back = int(str(time).split(".")[1])
        else:
            back = 0
        front = int(time)
        back *= 60
        back /= 100
        back = round(back)
        str(front)
        time = "%s:%s"%(front,back)
        artists_names_times.append([now["TPE1"].text[0], now["TIT2"].text[0], time])
        listsongs.append(files)

print(time_secs)
temp_db = []
count = 0
same = False
data = conn.execute('''SELECT * FROM ARTISTNAMES ORDER BY SCORE DESC''')

for row in data:
    count += 1
    temp_db.append(row[0])

best_artists = []
count = (count*10)/100
count = round(count)

for i in range(0,count):
        best_artists.append(temp_db[i])
print(best_artists)

for i in range (0, len(artists_names_times)):
    same = False
    for j in range (0, len(temp_db)):
        if artists_names_times[i][0] == temp_db[j]:
            same = True
    if same == False:
        conn.execute("INSERT INTO ARTISTNAMES(NAME, SCORE) VALUES(?,?)",(artists_names_times[i][0],0))
        temp_db.append(artists_names_times[i][0])
conn.commit()

del temp_db[0:len(temp_db)]
count = 0
best_songs = []
same = False
data = conn.execute('''SELECT * FROM SONGNAMES ORDER BY SCORE DESC''')

for row in data:
    count += 1
    temp_db.append(row[0])

count = (count*10)/100
count = round(count)

for i in range(0,count):
    best_songs.append(temp_db[i])
print(best_songs)


for i in range (0, len(artists_names_times)):
    same = False
    for j in range (0, len(temp_db)):
        if artists_names_times[i][1] == temp_db[j]:
            same = True
    if same == False:
        conn.execute("INSERT INTO SONGNAMES(NAME, SCORE) VALUES(?,?)",(artists_names_times[i][1],0))
        temp_db.append(artists_names_times[i][1])
conn.commit()

def randomize():
    global order
    order = random.sample(range(len(listsongs)), len(listsongs))
    count = round( (len(order)*25)/100 )

    removed_indexes = []
    for i in range(0, len(best_songs)):
        for j in range(0, len(artists_names_times)):
            if best_songs[i] == artists_names_times[j][1]:
                order.remove(j)
                removed_indexes.append(j)

    print("Best songs index", removed_indexes)
    better_songs_order = random.sample(removed_indexes, len(removed_indexes))
    print("Random order for best songs", better_songs_order)

    first25 = random.sample(range(0,count), len(better_songs_order))
    print("first25 places where songs will go", first25)

    for i in range(0,len(first25)):
        order.append(order[first25[i]])
        order[first25[i]] = better_songs_order[i]

    print("final order", order)


pygame.mixer.init()

selectsong = Listbox(top_frame, bd="0", width="25", bg="white")

for i in range (0,len(artists_names_times)):
    selectsong.insert(END, artists_names_times[i][1])

selectsong.grid(rowspan=3, column=0)
display_name = Label(top_frame, text="", font="none 20", bg="white")
display_name.grid(row=0, column=1, sticky="E", padx=(20,0))
display_time = Label(top_frame, text="", bg="white", font="none 12")
display_time.grid(row=1, column=1, sticky="E", padx=(20,0))
top_frame.grid_columnconfigure(1, weight=3)

order_index = 0
mins = 0
sec = 0
temp_runtime = 0
current_score = 0
called = False
original_score_done = False
final_score = 0

def update_db():
    conn.execute('''UPDATE SONGNAMES SET SCORE = ? WHERE NAME = ?''',(final_score, artists_names_times[order[order_index]][1],))
    print("Upgraded", final_score, artists_names_times[order[order_index]][1])
    conn.commit()


def give_score(runtime):
    global current_score
    global repetition
    global final_score
    global original_score_done
    if original_score_done == False:
        score = conn.execute(''' SELECT SCORE FROM SONGNAMES WHERE NAME = ?''', (artists_names_times[order[order_index]][1], ))
        for row in score:
            current_score = row[0]
        original_score_done = True
    else:
        if runtime > 0.10:
            final_score = current_score + runtime
            if final_score >= 10:
                final_score = 10
        elif runtime == -1:
            final_score = current_score - 0.5
            if final_score <= 0:
                final_score = 0
            conn.execute('''UPDATE SONGNAMES SET SCORE = ? WHERE NAME = ?''',(final_score, artists_names_times[order[order_index]][1],))
            print("Downgraded", final_score, artists_names_times[order[order_index]][1])
            conn.commit()


def update_queue_time():
    global i
    global order_index
    global mins
    global sec
    global time
    global temp_runtime
    if int(pygame.mixer.music.get_pos()) == -1:
        update_db()
        order_index += 1
        i = order[order_index]
        pygame.mixer.music.load(listsongs[i])
        pygame.mixer.music.play()
        display_name['text'] = artists_names_times[i][0] + " - " + artists_names_times[i][1]
        time = artists_names_times[order[i]][2]
        display_time['text'] = artists_names_times[i][2]
        mins = 0
        sec = 0

    if play:
        display_time['text'] = str(mins) + ":" + str(sec) + "/" + artists_names_times[i][2]
        sec += 1
        if sec == 60:
            mins += 1
            sec = 0
    runtime = ( (pygame.mixer.music.get_pos()/1000) / time_secs[order[order_index]] ) * 100
    runtime = round(runtime)
    runtime = runtime/100
    if runtime > temp_runtime:
        temp_runtime = runtime
        give_score(runtime)
    root.after(1000, update_queue_time)


def update_name():
    global called
    global temp_runtime
    global original_score_done
    temp_runtime = 0
    original_score_done = False
    display_name['text'] = artists_names_times[i][0] + " - " + artists_names_times[i][1]
    time = artists_names_times[i][2]
    display_time['text'] = time
    display_time['text'] = str(mins) + ":" + str(sec) + "/" + artists_names_times[i][2]
    if called == False:
        called = True
        update_queue_time()


def next():
    global i
    global order_index
    global play
    global mins
    global sec
    if temp_runtime <= 0.1:
        give_score(-1)
    elif temp_runtime > 0.1:
        update_db()
    order_index += 1
    i = order[order_index]
    mins = 0
    sec = 0
    pygame.mixer.music.load(listsongs[i])
    play = True
    pygame.mixer.music.play(0)
    update_name()



def prev():
    global i
    global order_index
    global play
    global mins
    global sec
    mins = 0
    sec = 0
    if temp_runtime > 0.1:
        update_db()
    order_index -= 1
    i = order[order_index]
    pygame.mixer.music.load(listsongs[i])
    play = True
    pygame.mixer.music.play(0)
    update_name()


def play_select(*args):
    global i
    global order_index
    global order
    global play
    global mins
    global sec
    mins = 0
    sec = 0
    if temp_runtime <= 0.1:
        give_score(-1)
    elif temp_runtime > 0.1:
        update_db()
    order_index = 0
    i = selectsong.curselection()[0]

    randomize()
    order.remove(i)
    order = [i] + order[:]

    pygame.mixer.music.load(listsongs[i])
    play = True
    pygame.mixer.music.play(0)
    update_name()


def play_pause():
    global play
    if play:
        pygame.mixer.music.pause()
        play = False

    else:
        pygame.mixer.music.unpause()
        play = True


randomize()
i = order[0]

pygame.mixer.music.load(listsongs[i])
pygame.mixer.music.play()
update_name()

prev_button = Button(bottom_frame, text="prev", command=prev, bg="white")
prev_button.grid(row=0, column=0, padx=(50,0))
pause_button = Button(bottom_frame, text="Play/Pause", command=play_pause, bg="white")
pause_button.grid(row=0, column=1)
next_button = Button(bottom_frame, text="next", command=next, bg="white")
next_button.grid(row=0, column=2)

os.chdir(temp_directory)

next_img = PhotoImage(file="nextcrop.png")
next_button.config(image=next_img)

prev_img = PhotoImage(file="prev crop.png")
prev_button.config(image=prev_img)

play_pause_img = PhotoImage(file="play pause - Copy crop.png")
pause_button.config(image=play_pause_img)

os.chdir(directory)

selectsong.bind("<Double-Button-1>",play_select)


root.mainloop()