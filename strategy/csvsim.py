import sim
import csv


COLS = [
    'match_num',
    'blue_score', 'red_score',
    'blue_scale', 'red_scale',
    'blue_own_switch', 'red_own_switch',
    'blue_other_switch', 'red_other_switch',
    'blue_boost_cubes', 'red_boost_cubes',
    'blue_force_cubes', 'red_force_cubes',
    'blue_climb_count', 'red_climb_count',
    'blue_rp', 'red_rp',
    'blue_initial', 'red_initial',
]


def make_row(run, blue, red):
    return [
        run, 
        blue['score'], red['score'], 
        blue['scale'], red['scale'],
        blue['own_switch'], red['own_switch'],
        blue['other_switch'], red['other_switch'],
        blue['boost_cubes'], red['boost_cubes'],
        blue['force_cubes'], red['force_cubes'],
        blue['climb_count'], red['climb_count'],
        blue['rp'], red['rp'],
        blue['initial_cubes'], red['initial_cubes'],
    ]


with open('stats.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(COLS)
    for run in range(1000):
        blue, red = sim.run_sim()
        writer.writerow(make_row(run, blue, red))
