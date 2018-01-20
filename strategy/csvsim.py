import sim
import csv


COLS = ['match_num', 'blue_score', 'red_score']


def make_row(run, blue, red):
    return [run, blue['score'], red['score']]


with open('stats.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(COLS)
    for run in range(1000):
        blue, red = sim.run_sim()
        writer.writerow(make_row(run, blue, red))
