#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from pandas import DataFrame
from numpy import array

if __name__ == '__main__':
    # Derived resource log RL
    rl = DataFrame(array([
        ['Pete', 'normal', 'register', 'afternoon'],
        ['Pete', 'normal', 'register', 'afternoon'],
        ['Ann', 'normal', 'contact', 'afternoon'],
        ['John', 'normal', 'check', 'morning'],
        ['Sue', 'normal', 'check', 'morning'],
        ['Bob', 'VIP', 'register', 'morning'],
        ['John', 'normal', 'decide', 'morning'],
        ['Sue', 'normal', 'decide', 'morning'],
        ['Mary', 'VIP', 'check', 'afternoon'],
        ['Mary', 'VIP', 'decide', 'afternoon']]),
        columns=['org:resource', 'case_type', 'activity_type', 'time_type']
    )

    # Organizational model OM
    from ordinor.org_model_miner import OrganizationalModel
    om = OrganizationalModel()
    groups = [
        {'Pete', 'Bob'},    # the registering team
        {'John', 'Sue'},    # the processing team (for normal orders)
        {'Mary'},           # the processing team (for VIP orders)
        {'Ann'}             # the contact team
    ]
    capabilities = [
        [('normal', 'register', 'afternoon'), ('VIP', 'register', 'morning')],
        [('normal', 'check', 'morning'), ('normal', 'decide', 'morning')],
        [('VIP', 'check', 'afternoon'), ('VIP', 'decide', 'afternoon')],
        [('normal', 'contact', 'afternoon')]
    ]
    for i in range(len(groups)):
        om.add_group(groups[i], capabilities[i])

    # Export the toy model
    with open('toy_example.om', 'w+') as fout:
        om.to_file_csv(fout)

    # Model evaluation (Global conformance measures)
    from ordinor.conformance import fitness, precision
    print('-' * 80)
    fitness_score = fitness(rl, om)
    print('Fitness\t\t= {:.3f}'.format(fitness_score))
    print()
    precision_score = precision(rl, om)
    print('Precision\t= {:.3f}'.format(precision_score))
    print()

    # Model analysis (Local conformance checking)
    from ordinor.analysis.group_profiles import \
        group_relative_focus, group_relative_stake, group_coverage
    for og_id, og in om.find_all_groups():
        index = groups.index(og)
        for mode in capabilities[index]:
            print('Group {}:\t[{}]\t --- {}'.format(
                og_id, ','.join(og), mode))
            print('\tRelFocus = {:.3f}'.format(
                group_relative_focus(og, mode, rl)))
            print('\tRelStake = {:.3f}'.format(
                group_relative_stake(og, mode, rl)))
            print('\tCov = {:.3f}'.format(
                group_coverage(og, mode, rl)))

