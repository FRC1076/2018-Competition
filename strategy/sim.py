import random
from random import *


def team_bs():   
    rpb = 0
    power_cubesb = randint(24, 36) 
    power_cubesr = 60 - power_cubesb
    boost_cubesb = boost_cubesr = 0
    force_cubesb = force_cubesr = 0
    score_r = score_b = 45

    scale_b = randint(3, power_cubesb)
    power_cubesb = power_cubesb - scale_b
    switch_b_b = randint(0,power_cubesb)
    power_cubesb = power_cubesb - switch_b_b
    switch_r_b = randint(0, power_cubesb)
    power_cubesb = power_cubesb - switch_r_b 
    if power_cubesb >= 3:
        force_cubesb = randint(0, 3)
        if force_cubesb == 1 and not switch_b_b:
            score_b = score_b + 15    
            score_r = 10 + score_r
        if force_cubesb == 2 and not scale_b and scale_r:
            score_b = score_b + 20
            score_r = score_r - 10
            if not scale_r and not scale_b:
                score_b = score_b + 10
        if force_cubesb == 3 and switch_b_b or not scale_b:
            score_b = score_b + 15
            if not scale_b and scale_r:
                score_b = score_b + 10
                score_r = score_r - 10
                if not scale_b and not scale_r:
                    score_b = score_b + 10
            if not switch_b_b:
                score_b = score_b + 10
        power_cubesb - force_cubesb == power_cubesb
    if power_cubesb >= 3:
        boost_cubesb = randint(0, 3)
        if boost_cubesb == 1 and switch_b_b:
            score_b = score_b + 15
        if boost_cubesb == 2 and scale_b:
            score_b = score_b + 20
        if boost_cubesb == 3 and switch_b_b or scale_b:
            score_b = score_b + 15
            if scale_b:
                score_b = score_b + 10 
            if switch_b_b:
                score_b = score_b + 10
        power_cubesb = power_cubesb - boost_cubesb
    robo1_blue = randint(1,3)
    robo2_blue = randint(1,3)
    robo3_blue = randint(1,3)
    z = 0
    if robo1_blue == 1:
        z = z + 1
    if robo2_blue == 1:
        z = z + 1
    if robo3_blue == 1:
        z = z + 1
    if z == 2 and power_cubesb >= 3:
        score_b = score_b + 105
        power_cubesb = power_cubesb - 3
        rpb = rpb + 1
    if z == 2 and power_cubesb <= 3:
        score_b = score_b + 60
    if z == 3:
        score_b = score_b + 90
        rpb = rpb + 1
    if z == 1 and power_cubesb >= 3:
     score_b = score_b + 75
     power_cubesb = power_cubesb - 3
    if z == 1 and power_cubesb <= 3:
     score_b = score_b + 30
    if z == 0 and power_cubesb >= 3:
        score_b = score_b + 45
        power_cubesb = power_cubesb - 3
    
 
    scale_r = randint(3, power_cubesr)
    power_cubesr = power_cubesr - scale_r
    switch_r_r = randint(0,power_cubesr)
    power_cubesr = power_cubesr - switch_r_r
    switch_b_r = randint(0, power_cubesr)
    if power_cubesr >= 3:
        force_cubesr = randint(0, 3)
        if force_cubesr == 1 and not switch_r_r:
            score_r = score_r + 15
            score_b = score_b - 10
        if force_cubesr == 2 and not scale_r and scale_b:
            score_r = score_r + 20
            score_b = score_b - 10
            if not scale_r and not scale_b:
                score_r = score_r + 20
        if force_cubesr == 3 and switch_r_r or not scale_r:
            score_r = score_r + 15
            if not scale_r and scale_b:
                score_r = score_r + 10
                score_b = score_b - 10
            if not scale_b and not scale_r:
                score_r = score_r + 10
            if not switch_r_r:
                score_r = score_r + 10
        power_cubesr = power_cubesr - force_cubesr
    if power_cubesr >= 3:
        boost_cubesr = randint(0, 3)
        if boost_cubesr == 1 and switch_r_r:
            score_r = score_r + 15
        if boost_cubesr == 2 and scale_r:
            score_r = score_r + 20
        if boost_cubesr == 3 and switch_r_r or scale_r:
            score_r = score_r + 15
            if scale_r:
                score_r = score_r + 10
            if switch_r_r:
                score_r = score_r + 10
        power_cubesr = power_cubesr - boost_cubesr
    robo1_red = randint(1,3)
    robo2_red = randint(1,3)
    robo3_red = randint(1,3)
    zr = 0
    rpb = 0
    rpr = 0
    if robo1_red == 1:
        zr = zr + 1
    if robo2_red == 1:
        zr = zr + 1
    if robo3_red == 1:
        zr = zr + 1
    if zr == 2 and power_cubesr >= 3:
        score_r = score_r + 105
        power_cubesr = power_cubesr - 3
        rpr = rpr + 1
    if zr == 2 and power_cubesr <= 3:
        score_r = score_r + 60
    if zr == 3:
        score_r = score_r + 90
        rpr = rpr + 1
    if zr == 1 and power_cubesr >= 3:
        score_r = score_r + 75
        power_cubesr = power_cubesr - 3
    if zr == 1 and power_cubesr <= 3:
        score_r = score_r + 30
    if zr == 0 and power_cubesr >= 3:
        score_r = score_r + 45
        power_cubesr = power_cubesr - 3

    if scale_r > scale_b:
        score_r = score_r + 165
    elif scale_b > scale_r:
        score_b = score_b + 165

    if switch_r_r > switch_r_b:
        score_r = score_r + 135

    if switch_b_b > switch_b_r:
        score_b = score_b + 135

    if score_b > score_r:
        rpb = rpb + 2
    elif score_r > score_b:
        rpr = rpr + 2
    else:
        rpb = rpb + 1
        rpr = rpr + 1
    print ("This is the data for blue:" "score:", score_b, "scale weight:", scale_b, " weight on home side:", switch_b_b, " weight on opposing side:", switch_r_b," cubes used for boost powerup:", boost_cubesb, "cubes used for force powerup:" ,force_cubesb, "number of robots who successfully climbed the tower:", z, "ranking points:", rpb)             
    print (" this is the data for red:", "score", score_r, "scale weight:", scale_r, "weight on home side:", switch_r_r, "weight on opposing side:", switch_b_r, "cubes used for boost powerup:", boost_cubesr, "cubes used for force powerup:",force_cubesr, "number of robots who successfully climbed the tower:", zr, "ranking points", rpr)

team_bs()
    
