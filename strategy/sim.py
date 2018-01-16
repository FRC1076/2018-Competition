import random
from random import *


def power_cube_distribution(power_cubes):
    scale = randint(3, power_cubes)
    power_cubes -= scale
    own_switch = randint(0, power_cubes)
    power_cubes -= own_switch
    other_switch = randint(0, power_cubes)
    power_cubes -= other_switch
    force_cubes = randint(0, min(3, power_cubes))
    power_cubes -= force_cubes
    boost_cubes = randint(0, min(3, power_cubes))
    power_cubes -= boost_cubes
    return power_cubes, scale, own_switch, other_switch, force_cubes, boost_cubes


def determine_owners(bswitch_b, bswitch_r, rswitch_b, rswitch_r, own_scale, other_scale):
    if bswitch_b > bswitch_r:
        owner_b = 'blue'
    elif bswitch_r > bswitch_b:
        owner_b = 'red'
    else:
        owner_b = None

    if rswitch_b > rswitch_r:
        owner_r = 'blue'
    elif rswitch_r >rswitch_b:
        owner_r = 'red'
    else:
        owner_r = None

    if own_scale > other_scale:
        owner_scale = 'blue'
    elif other_scale > own_scale:
        owner_scale = 'red'
    else:
        owner_scale = None

    return owner_b, owner_r, owner_scale


def force_cubes(force_cubes, our_score, other_score, own_switch, own_scale):
    """
    If you have n cubes, you get the following effects:
    1. Take control of your switch for 10 seconds
    2. Take control of the scale for 10 seconds
    3. Take control of both for 10 seconds
    """
    # We're stealing our switch
    if not own_switch and force_cubes in (1, 3):
        our_score += 10
        other_score -= 10
    # We're stealing the scale
    if not own_scale and force_cubes in (2, 3):
        our_score += 10
        other_score -= 10
    
    return our_score, other_score


def boost_cubes(boost_cubes, own_switch, our_score, own_scale, other_score):
    if boost_cubes == 1 and own_switch:
        our_score += 15
    if boost_cubes == 2 and own_scale:
        our_score += 20
    if boost_cubes == 3 and own_switch or own_scale:
        our_score += 15
        if own_scale:
            our_score += 10 
        if own_switch:
            our_score += 10
    return our_score, other_score

def climbing(rp, power_cubes, score):
    robo1_blue = randint(1, 3)
    robo2_blue = randint(1, 3)
    robo3_blue = randint(1, 3)
    z = 0
    if robo1_blue > 1:
        z += 1
    if robo2_blue > 1:
        z += 1
    if robo3_blue > 1:
        z += 1
    if z == 2 and power_cubes >= 3:
        score += 105
        power_cubes -= 3
        rp += 1
    if z == 2 and power_cubes <= 3:
        score +=  60
    if z == 3:
        score += 90
        rp +=  1
    if z == 1 and power_cubes >= 3:
        score += 75
        power_cubes -= 3
    if z == 1 and power_cubes <= 3:
        score += 30
    if z == 0 and power_cubes >= 3:
        score += 45
        power_cubes -= 3
    return z, rp, power_cubes, score

def points_for_possesion():
    if own_scale > other:
        score_r += 165
    elif own_scale > other_scale:
        score_b += 165

    if rswitch_r > rswitch_b:
        score_r += 135
    elif bswitch_b > bswitch_r:
        score_b += 135
def run_sim():
    rpb = rpr = 0
    power_cubesb = randint(24, 36) 
    power_cubesr = 60 - power_cubesb
    boost_cubesb = boost_cubesr = 0
    force_cubesb = force_cubesr = 0
    score_r = score_b = 45
    
    power_cubesb, own_scale, bswitch_b, rswitch_b, force_cubesb, boost_cubesb = power_cube_distribution(power_cubesb)
    zb, rpb, power_cubesb, score_b = climbing(rpb, power_cubesb, score_b)

    power_cubesr, other_scale, rswitch_r, bswitch_r, force_cubesr, boost_cubesr = power_cube_distribution(power_cubesr) 
    zr, rpr, power_cubesr, score_r = climbing(rpr, power_cubesr, score_r)
    
    owner_b, owner_r, owner_scale = determine_owners(bswitch_b, bswitch_r, rswitch_b, rswitch_r, own_scale, other_scale)

    if other_scale > own_scale:
        score_r += 165
    elif own_scale > other_scale:
        score_b += 165

    if rswitch_r > rswitch_b:
        score_r += 135
    elif bswitch_b > bswitch_r:
        score_b += 135

    score_b, score_r = force_cubes(force_cubesb, score_b, score_r, owner_b == 'blue', owner_scale == 'blue')
    score_r, score_b = force_cubes(force_cubesr, score_r, score_b, owner_r == 'red', owner_scale == 'red')
    score_b, score_r = boost_cubes(boost_cubesb, score_b, score_r, owner_b == 'blue', owner_scale == 'blue')
    score_r, score_b = boost_cubes(boost_cubesr, score_r, score_b, owner_r == 'red', owner_scale == 'red')
    if score_b > score_r:
        rpb += 2
    elif score_r > score_b:
        rpr += 2
    else:
        rpb += 1
        rpr += 1
    print(
        "This is the data for blue:",
        "score:", score_b,
        "scale weight:", own_scale,
        "weight on home side:", bswitch_b,
        "weight on opposing side:", rswitch_b,
        "cubes used for boost powerup:", boost_cubesb,
        "cubes used for force powerup:", force_cubesb,
        "number of robots who successfully climbed the tower:", zb,
        "ranking points:", rpb,
    )
    print(
        "This is the data for red:", 
        "score", score_r,
        "scale weight:", other_scale,
        "weight on home side:", rswitch_r,
        "weight on opposing side:", bswitch_r,
        "cubes used for boost powerup:", boost_cubesr,
        "cubes used for force powerup:", force_cubesr,
        "number of robots who successfully climbed the tower:", zr,
        "ranking points", rpr,
    )

if __name__ == '__main__':
    run_sim()
