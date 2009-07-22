#!/usr/bin/env python2.5

import random, sys

nats = []
nats_by_name = {}
you = 0
last_input = None
forces = []

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

def init():
    global nats, nats_by_name, you
    #              country    adj        money    pop          soldiers ts
    nats = [Nation('USA',     'American',200000,  300000000,   3000000, 5),
            Nation('France',    'French',  1000,   50000000,    500000, 3),
            Nation('Germany',   'German',    50,   80000000,   2000000, 4),
            Nation('Mexico',   'Mexican',    50,   30000000,     10000, 1),
            Nation('China',    'Chinese',  5000, 1300000000,   5000000, 2)]
    for nat in nats:
        nats_by_name[nat.name] = nat
    you = 0

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

def cmd_invade(args):
    name = args[1]
    #defender = nat_with_name(name)
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
        print '%s invades %s with %s soldiers' % (attacker, defender, force_size)
        f = Force(attacker, force_size, defender)
        forces.append(f)
    else:
        print '%s sends %s additional soldiers to %s' % (attacker, force_size, defender)
        f.soldiers += force_size
cmd_inv = cmd_invade

def cmd_withdraw(args):
    name = args[1]
    #target_nat = nat_with_name(name)
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
        print '%s withdraws all but min required occupation force from %s (%s %s soldiers)' % (force_owner.name, target_nat.name, force_owner.adj, wd_amount)
    else:
        wd_amount = f.soldiers
        print '%s withdraws all forces from %s (%s %s soldiers)' % (force_owner.name, target_nat.name, force_owner.adj, wd_amount)
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
        print 'eval %s force in %s' % (f.owner, f.target_nat)
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
        print 'In the war in %s the losses are %s %s soldiers and %s %s soldiers' % (defender.name, atk_kills, defender.adj, def_kills, attacker.adj)
        if defender.soldiers <= 0:
            defender.soldiers = 0
            defender.conquered = attacker
            print '%s conquered by %s' % (defender.name, attacker.name)


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
            print '%s rebels because not enough occupying soldiers (was %s, needed %s)' % (nat.name, occ_soldiers, min_req_occ_soldiers)

def cmd_quit(args):
    print 'quitting...'
    sys.exit(0)
cmd_q = cmd_quit

shortcuts = {'.' : 'again'}

def draw_ui():
    fmt = '%9s %9s %8s %10s %9s %2s'
    print fmt % ('country','owner','money','population','soldiers','ts')
    for nat in nats:
        name = '%s' % nat.name
        money = '$%sm' % nat.money
        owner = nat.conquered and nat.conquered.name or ''
        print fmt % (name, owner, money, nat.pop, nat.soldiers, nat.troop_skill),
        invaders = ''
        for f in forces:
            if f.target_nat == nat:
                invaders += ' (%s %s soldiers)' % (f.soldiers, f.owner.adj)
        print invaders
    print ''

def handle_input():
    global last_input
    input = sys.stdin.readline().strip()
    print ''
    args = input.split()
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
    rebellion()

def main():
    init()
    print '-' * 80 + '\n\nWarconomy\n'
    print 'You run %s. Conquer the world!\n' % nats[you].name
    while True:
        draw_ui()
        print '-' * 40
        print 'Command: ',
        handle_input()
        print '-' * 40

if __name__ == '__main__':
    main()
