#!/usr/bin/env python2.5

from __future__ import with_statement
import os, pickle, random, sys

nats = []
nats_by_name = {}
you = 0
last_input = None
forces = []
stances = {}

class Nation:
    name = ''
    money = 1000

    def __init__(self, name, adj, money, pop, soldiers, troop_skill):
        self.name = name
        self.adj = adj
        self.money = money
        self.pop = pop
        self.soldiers = soldiers
        self.troop_skill = troop_skill # represents sum effects of: tech, morale, training, initiative, fitness, leadership
        self.conquered = None

    def __str__(self):
        return self.name


class Force:
    def __init__(self, owner, soldiers, target_nat):
        self.owner = owner
        self.soldiers = soldiers
        self.target_nat = target_nat

STANCE_EXTERMINATE = 0
STANCE_WAR = 1
STANCE_BRINK = 2
STANCE_HOSTILE = 3
STANCE_UNFRIENDLY = 4
STANCE_WARY = 5
STANCE_NEUTRAL = 6
STANCE_FRIENDLY = 7
STANCE_MINOR_ALLY = 8
STANCE_CLOSE_MAJOR_ALLY = 9
STANCE_BRETHREN = 10
stance_codes = ['EXT','WAR','BNK','HOS','UNF','WRY','NEU','FRI','MIN','MAJ','BRE']

def init():
    global nats, nats_by_name, you, stances
    # pop from Wikipedia, for 2009
    # soldiers from 'Total Troops' column of web page: http://en.wikipedia.org/wiki/List_of_countries_by_size_of_armed_forces
    # key: country     adj          money         pop          soldiers ts
    nats = [
    Nation('USA',             'US', 2000000000000,  306963000,   3385400, 5),
    Nation('France',      'French',  100000000000,   65073482,    779450, 3),
    Nation('Germany',     'German',  250000000000,   82060000,    606362, 4),
    Nation('Mexico',     'Mexican',   10000000000,  111211789,    517770, 1),
    Nation('China',      'Chinese', 1000000000000, 1338612968,   7024000, 3),
    Nation('Russia',     'Russian',  100000000000,  142008838,   3796100, 4),
    Nation('Iran',       'Iranian',   10000000000,   70495782,   1695000, 2),
    Nation('Japan',     'Japanese',  300000000000,  127433494,    296550, 3),
    Nation('India',       'Indian',  100000000000, 1100000000,   3773300, 3),
    Nation('Brazil',       'Braz.',   10000000000,  191241714,   1687600, 1),
    Nation('UK',              'UK',  200000000000,   61612300,    421830, 5),
    Nation('N. Korea', 'N. Korean',    1000000000,   22666000,   5995000, 2),
    ]
    for nat in nats:
        nats_by_name[nat.name] = nat
    you = 0
    stances = {}
    for n1 in nats:
        stances[n1] = {}
        #print 'stances[n1] = %s, where n1 is %s' % (stances[n1], n1)
        for n2 in nats:
            stance = STANCE_NEUTRAL
            if n2 == n1:
                stance = STANCE_BRETHREN
            stances[n1][n2] = stance
            #print 'stances[n1][n2] = %s' % stances[n1][n2]
    mutual_stance('USA', 'UK', STANCE_CLOSE_MAJOR_ALLY)
    mutual_stance('USA', 'Japan', STANCE_CLOSE_MAJOR_ALLY)
    mutual_stance('USA', 'Germany', STANCE_MINOR_ALLY)
    mutual_stance('USA', 'France', STANCE_MINOR_ALLY)
    mutual_stance('USA', 'Mexico', STANCE_FRIENDLY)
    mutual_stance('USA', 'India', STANCE_FRIENDLY)
    mutual_stance('USA', 'Brazil', STANCE_FRIENDLY)
    mutual_stance('USA', 'China', STANCE_WARY)
    mutual_stance('USA', 'Russia', STANCE_WARY)
    mutual_stance('USA', 'Iran', STANCE_UNFRIENDLY)
    mutual_stance('USA', 'N. Korea', STANCE_UNFRIENDLY)

def mutual_stance(n1_name, n2_name, stance):
    global stances
    #print '%s, %s, %s' % (n1_name, n2_name, stance)
    n1 = nats_by_name[n1_name]
    n2 = nats_by_name[n2_name]
    #print '%s, %s' % (hex(id(n1)), hex(id(n2)))
    stances[n1][n2] = stance
    stances[n2][n1] = stance

def abbrev_num(qty):
    #print 'qty %s' % qty
    factor = 1
    abbrev_amount = None
    while True:
        abbrev_amount = float(qty) / float(factor)
        if abbrev_amount >= 1000:
            factor *= 1000
        else:
            break
    units = {1:'', 1000:'k', 1000000:'m', 1000000000:'b', 1000000000000:'t'}
    unit = None
    if factor in units:
        unit = units[factor]
    else:
        unit = '?'
    amt = '%.1f' % abbrev_amount
    if amt.endswith('.0'):
        amt = amt[:-2]
    return '%s%s' % (amt, unit)

def nat_with_name(name):
    for k in nats_by_name.keys():
        if name.lower() == k.lower():
            return nats_by_name[k]
    return None

def nats_with_name_starting_with(prefix):
    ns = []
    for k in nats_by_name.keys():
        if k.lower().startswith(prefix.lower()):
            nat = nats_by_name[k]
            ns.append(nat)
    return ns

def nat_with_name_starting_with(prefix):
    ns = nats_with_name_starting_with(prefix)
    if len(ns) == 1:
        return ns[0]
    else:
        return None

def cmd_do_nothing(args):
    tick()
    print '-' * 40
cmd_n = cmd_do_nothing

def cmd_raise_soldiers(args):
    new_soldiers = int(args[1])
    cost = new_soldiers * 100000
    nat = nats[you]
    if cost <= nat.money:
        nat.money -= cost
        nat.soldiers += new_soldiers
        print '%s raises %s more soldiers costing $%s' % (nat, abbrev_num(new_soldiers), abbrev_num(cost))
    else:
        print '%s cannot afford the $%s cost to raise %s more soldiers' % (nat, abbrev_num(cost), abbrev_num(new_soldiers))
cmd_s = cmd_raise_soldiers

def cmd_invade(args):
    name = args[1]
    defender = nat_with_name_starting_with(name)
    if not defender:
        print 'that is not a unique country: %s' % name
        return
    attacker = nats[you]
    if attacker is defender:
        print '%s cannot invade itself' % attacker.name
        return
    force_size = attacker.soldiers / 2
    attacker.soldiers -= force_size
    f = get_force_there_already(attacker,defender)
    if not f:
        print '%s invades %s with %s soldiers' % (attacker, defender, abbrev_num(force_size))
        f = Force(attacker, force_size, defender)
        forces.append(f)
    else:
        print '%s sends %s additional soldiers to %s' % (attacker, abbrev_num(force_size), defender)
        f.soldiers += force_size
    mutual_stance(attacker.name, defender.name, STANCE_WAR)
cmd_inv = cmd_invade

def cmd_withdraw(args):
    name = args[1]
    target_nat = nat_with_name_starting_with(name)
    if not target_nat:
        print 'that is not a unique country: %s' % name
        return
    force_owner = nats[you]
    if force_owner == target_nat:
        print 'you cannot withraw forces from yourself'
        return
    f = get_force_there_already(force_owner,target_nat)
    if not f:
        print '%s has no force in %s' % (force_owner.name, target_nat.name)
        return
    min_req_occ_soldiers = get_min_req_occupying_force_size(target_nat)
    # assumes we have only one force there
    if f.soldiers > min_req_occ_soldiers:
        wd_amount = f.soldiers - min_req_occ_soldiers
        print '%s withdraws all but min required occupation force (of %s soldiers) from %s (%s soldiers)' % (force_owner.name, abbrev_num(min_req_occ_soldiers), target_nat.name, abbrev_num(wd_amount))
    else:
        wd_amount = f.soldiers
        print '%s withdraws all forces from %s (%s %s soldiers)' % (force_owner.name, target_nat.name, force_owner.adj, abbrev_num(wd_amount))
    f.soldiers -= wd_amount
    force_owner.soldiers += wd_amount
    if f.soldiers == 0:
        forces.remove(f)
cmd_wd = cmd_withdraw

def calc_kills(shooting_soldiers, skill):
    kills = 0
    for i in xrange(shooting_soldiers):
        if random.randrange(0,10) < skill:
            kills += 1
    return kills

def get_force_there_already(owner, where):
    for f in forces:
        if f.owner == owner and f.target_nat == where:
            return f
    return None

def conflicts():
    print 'conflicts'
    for f in forces:
        print 'eval %s force in %s' % (f.owner.adj, f.target_nat)
        attacker = f.owner
        defender = f.target_nat
        if defender.conquered and defender.soldiers == 0:
            continue
        atk_kills = calc_kills(f.soldiers, attacker.troop_skill)
        def_kills = calc_kills(defender.soldiers, defender.troop_skill)
        if atk_kills > defender.soldiers:
            atk_kills = defender.soldiers
        if def_kills > f.soldiers:
            def_kills = f.soldiers
        defender.soldiers -= atk_kills
        f.soldiers -= def_kills
        print 'In the war in %s the losses are %s %s soldiers and %s %s soldiers' % (defender.name, abbrev_num(atk_kills), defender.adj, abbrev_num(def_kills), attacker.adj)
        if defender.soldiers <= 0:
            defender.soldiers = 0
            defender.conquered = attacker
            print '%s conquered by %s' % (defender.name, attacker.name)

def looting():
    for nat in nats:
        if not nat.conquered: continue
        looted_money = nat.money / 4
        nat.money -= looted_money
        nat.conquered.money += looted_money
        print '%s loots $%s from conquered %s' % (nat.conquered, abbrev_num(looted_money), nat)

def get_total_occupying_soldiers(nat):
    total = 0
    for f in forces:
        if f.target_nat == nat:
            total += f.soldiers
    return total

def get_min_req_occupying_force_size(nat):
    return nat.pop / 100

def rebellion():
    print 'rebellion'
    for nat in nats:
        if not nat.conquered: continue
        occ_soldiers = get_total_occupying_soldiers(nat)
        min_req_occ_soldiers = get_min_req_occupying_force_size(nat)
        if occ_soldiers < min_req_occ_soldiers:
            nat.conquered = None
            new_rebels = nat.pop / 100000
            nat.soldiers += new_rebels
            print '%s rebels (gains %s fighters) because not enough occupying soldiers (was %s, needed %s)' % (nat, new_rebels, occ_soldiers, min_req_occ_soldiers)

def cmd_quit(args):
    print 'quitting...'
    sys.exit(0)
cmd_q = cmd_quit

shortcuts = {'.' : 'again'}

def draw_ui():
    fmt = '%9s %6s %9s %7s %6s %6s %2s %6s'
    print fmt % ('country','stance','owner','money','pop.','troops','ts','occreq')
    for nat in nats:
        name = '%s' % nat.name
        if nat is nats[you]:
            name = '*%s*' % name
        stance = '%s/%s' % (stances[nat][nats[you]], stances[nats[you]][nat])
        money = '$%s' % abbrev_num(nat.money)
        owner = nat.conquered and nat.conquered.name or ''
        pop = abbrev_num(nat.pop)
        soldiers = abbrev_num(nat.soldiers)
        occ_req = abbrev_num(get_min_req_occupying_force_size(nat))
        print fmt % (name, stance, owner, money, pop, soldiers, nat.troop_skill, occ_req),
        invaders = ''
        for f in forces:
            if f.target_nat == nat:
                invaders += ' (%s %s soldiers)' % (abbrev_num(f.soldiers), f.owner.adj)
        print invaders
    print ''

def handle_input():
    global last_input
    input = sys.stdin.readline().strip()
    print ''
    args = input.split()
    if len(args) == 0:
        print 'no input'
        return
    cmd = args[0]
    if cmd in shortcuts:
        cmd = shortcuts[cmd]
    if cmd == 'again':
        if last_input is not None:
            args = last_input.split()
            cmd = args[0]
    else:
        last_input = input
    cmd_fn_name = 'cmd_%s' % cmd
    if cmd_fn_name in globals():
        fn = globals()[cmd_fn_name]
        fn(args)
    print '-' * 40

def tick():
    print 'Time advances...'
    conflicts()
    looting()
    rebellion()

class State: pass

SAVE_FILENAME = 'savedgame'

def save():
    state = State()
    state.nats = nats
    state.nats_by_name = nats_by_name
    state.you = you
    state.last_input = last_input
    state.forces = forces
    state.stances = stances
    with open(SAVE_FILENAME,'w') as f:
        pickle.dump(state,f)

def restore():
    fpath = SAVE_FILENAME
    if not os.path.isfile(fpath):
        return
    global nats, nats_by_name, you, last_input, forces, stances
    with open(fpath,'r') as f:
        state = pickle.load(f)
        nats = state.nats
        nats_by_name = state.nats_by_name
        you = state.you
        last_input = state.last_input
        forces = state.forces
        stances = state.stances

def main():
    init()
    restore()
    print '-' * 80 + '\n\nWarconomy\n'
    print 'You run %s. Conquer the world!\n' % nats[you].name
    while True:
        draw_ui()
        print '-' * 40
        print 'Command: ',
        handle_input()
        save()
        print '-' * 40

if __name__ == '__main__':
    main()
