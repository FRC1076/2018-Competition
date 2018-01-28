import random


def split_cubes():
    power_cubesb = power_cubesr = 0
    for i in range(60):
        if random.randint(0, 1):
            power_cubesb += 1
        else:
            power_cubesr += 1
    return power_cubesb, power_cubesr


def power_cube_distribution(power_cubes):
    scale = random.randint(3, power_cubes)
    power_cubes -= scale
    own_switch = random.randint(0, power_cubes)
    power_cubes -= own_switch
    other_switch = random.randint(0, power_cubes)
    power_cubes -= other_switch
    force_cubes = random.randint(0, min(3, power_cubes))
    power_cubes -= force_cubes
    boost_cubes = random.randint(0, min(3, power_cubes))
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


def boost_cubes(boost_cubes, our_score, other_score, own_switch, own_scale):
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
    robo1 = random.randint(1, 3)
    robo2 = random.randint(1, 3)
    robo3 = random.randint(1, 3)
    climb_count = 0
    if robo1 > 1:
        climb_count += 1
    if robo2 > 1:
        climb_count += 1
    if robo3 > 1:
        climb_count += 1
    if climb_count == 2 and power_cubes >= 3:
        score += 105
        power_cubes -= 3
        rp += 1
    if climb_count == 2 and power_cubes <= 3:
        score +=  60
    if climb_count == 3:
        score += 90
        rp +=  1
    if climb_count == 1 and power_cubes >= 3:
        score += 75
        power_cubes -= 3
    if climb_count == 1 and power_cubes <= 3:
        score += 30
    if climb_count == 0 and power_cubes >= 3:
        score += 45
        power_cubes -= 3
    return climb_count, rp, power_cubes, score


def print_data(data):
    print(
        "score:", data['score'],
        "scale weight:", data['scale'],
        "weight on home side:", data['own_switch'],
        "weight on opposing side:", data['other_switch'],
        "cubes used for boost powerup:", data['boost_cubes'],
        "cubes used for force powerup:", data['force_cubes'],
        "number of robots who successfully climbed the tower:", data['climb_count'],
        "ranking points:", data['rp'],
    )


def run_sim():
    rpb = rpr = 0
    score_r = score_b = 45

    initial_power_cubesb, initial_power_cubesr = split_cubes()
    
    power_cubesb, scale_b, bswitch_b, rswitch_b, force_cubesb, boost_cubesb = power_cube_distribution(initial_power_cubesb)
    power_cubesr, scale_r, rswitch_r, bswitch_r, force_cubesr, boost_cubesr = power_cube_distribution(initial_power_cubesr)

    climb_countb, rpb, power_cubesb, score_b = climbing(rpb, power_cubesb, score_b) 
    climb_countr, rpr, power_cubesr, score_r = climbing(rpr, power_cubesr, score_r)
    
    owner_b, owner_r, owner_scale = determine_owners(bswitch_b, bswitch_r, rswitch_r, rswitch_b, scale_b, scale_r)

    if scale_r > scale_b:
        score_r += 165
    elif scale_b > scale_r:
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

    blue_data = {
        'color': 'blue',
        'initial_cubes': initial_power_cubesb,
        'score': score_b,
        'scale': scale_b,
        'bswitch': bswitch_b,
        'rswitch': rswitch_b,
        'own_switch': bswitch_b,
        'other_switch': rswitch_b,
        'boost_cubes': boost_cubesb,
        'force_cubes': force_cubesb,
        'climb_count': climb_countb,
        'rp': rpb,
    }

    red_data = {
        'color': 'red',
        'initial_cubes': initial_power_cubesr,
        'score': score_r,
        'scale': scale_r,
        'rswitch': rswitch_r,
        'bswitch': bswitch_r,
        'own_switch': rswitch_r,
        'other_switch': bswitch_r,
        'boost_cubes': boost_cubesr,
        'force_cubes': force_cubesr,
        'climb_count': climb_countr,
        'rp': rpr,
    }
    
    return blue_data, red_data
    
if __name__ == '__main__':
    blue, red = run_sim()
    print("This is the data for blue:")
    print_data(blue)
    print("This is the data for red:")
    print_data(red)
