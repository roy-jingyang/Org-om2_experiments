#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('fn_event_log', 
    help='Path to input log file')
parser.add_argument('fnout_org_model', 
    help='Path to output model file')

args = parser.parse_args()

fn_event_log = args.fn_event_log
fnout_org_model = args.fnout_org_model

if __name__ == '__main__':
    # read event log as input
    from ordinor.io import read_xes
    el = read_xes(fn_event_log)

    # 1. Learn execution contexts
    from ordinor.execution_context import \
        ATonlyMiner, FullMiner, TraceClusteringFullMiner
    print('Input a number to choose a solution:')
    print('\t0. ATonly')
    print('\t1. CT+AT+TT (case attribute)')
    print('\t2. CT+AT+TT (trace clustering)')
    ec_learning_option = int(input())

    if ec_learning_option == 0:
        ec_miner = ATonlyMiner(el)

    elif ec_learning_option == 1:
        print(el.columns)
        print('\tSpecify the name of the case attribute:', end=' ')
        sp_case_attr_name = input()
        print('\tInput a number to choose a desired time unit:')
        units = ['hour', 'day', 'weekday']
        for i, unit in enumerate(units):
            print('\t\t{}. {}'.format(i, unit))
        sp_time_unit = units[int(input())]
        ec_miner = FullMiner(el,
            case_attr_name=sp_case_attr_name,
            resolution=sp_time_unit)

    elif ec_learning_option == 2:
        print('Input the path to the trace clustering report file:', end=' ')
        fn_partition = input()
        print('\tInput a number to choose a desired time unit:')
        units = ['hour', 'day', 'weekday']
        for i, unit in enumerate(units):
            print('\t\t{}. {}'.format(i, unit))
        sp_time_unit = units[int(input())]
        ec_miner = TraceClusteringFullMiner(el,
            fn_partition=fn_partition,
            resolution=sp_time_unit)
    else:
        raise ValueError('Option not recognized')

    with open(fnout_org_model + '.co_mappings', 'wb') as fout:
        ec_miner.to_file(fout)
        print('\n[Execution context mappings exported]')
    # Derive resource log
    rl = ec_miner.derive_resource_log(el)


    # 2. Discover organizational groups
    print('Input a number to choose a solution:')
    print('\t0. AHC: Hierarchical Organizational Mining (Song and van der Aalst, 2008)')
    print('\t1. MOC: Model based Overlapping Clustering (Yang et al., 2018)')
    mining_option = int(input())

    if mining_option in [10, 11, 13, 14, 16]:
        raise NotImplementedError

    if mining_option == 0:
        print('Input desired range (e.g. [low, high)) of number of groups:',
            end=' ')
        num_groups = input()
        num_groups = num_groups[1:-1].split(',')
        num_groups = list(range(int(num_groups[0]), int(num_groups[1])))

        # build profiles
        from ordinor.org_model_miner.resource_features import direct_count
        profiles = direct_count(rl, scale='log')
        from ordinor.org_model_miner.group_discovery import ahc
        ogs = ahc(profiles, num_groups, method='ward')

    elif mining_option == 1:
        print('Input desired range (e.g. [low, high)) of number of groups:',
            end=' ')
        num_groups = input()
        num_groups = num_groups[1:-1].split(',')
        num_groups = list(range(int(num_groups[0]), int(num_groups[1])))

        # build profiles
        from ordinor.org_model_miner.resource_features import direct_count
        profiles = direct_count(rl, scale='log')

        from ordinor.org_model_miner.group_discovery import moc
        ogs = moc(profiles, num_groups, init='kmeans')
    else:
        raise Exception('Failed to recognize input option!')


    # 3. Assign execution contexts to groups
    from ordinor.org_model_miner.group_profiling import\
        full_recall, overall_score
    print('Input a number to choose a solution:')
    print('\t0. FullRecall')
    print('\t1. OverallScore')
    assignment_option = int(input())
    if assignment_option in []:
        raise NotImplementedError
    elif assignment_option == 0:
        om = full_recall(ogs, rl)
    elif assignment_option == 1:
        print('Input desired weighting value ranged (0.0, 1.0) for Group Relative Stake:', 
            end=' ')
        sp_w1 = float(input())
        print('Weighting value for Group Coverage' +
            ' derived automatically: {}'.format(1.0 - sp_w1))

        print('Input a threshold value ranged [0.0, 1.0):', end=' ')
        sp_p = float(input())
        om = overall_score(ogs, rl, p=sp_p, w1=sp_w1)

    # Evaluate discovery result

    print('-' * 80)
    measure_values = list()
    
    from ordinor.conformance import fitness, precision
    fitness_score = fitness(rl, om)
    print('Fitness\t\t= {:.3f}'.format(fitness_score))
    measure_values.append(fitness_score)
    print()
    precision_score = precision(rl, om)
    print('Precision\t= {:.3f}'.format(precision_score))
    measure_values.append(precision_score)
    print()

    '''
    # Overlapping Density & Overlapping Diversity (avg.)
    k = om.group_number
    resources = om.resources
    n_ov_res = 0
    n_ov_res_membership = 0
    for r in resources:
        n_res_membership = len(om.find_groups(r))
        if n_res_membership == 1:
            pass
        else:
            n_ov_res += 1
            n_ov_res_membership += n_res_membership

    ov_density = n_ov_res / len(resources)
    avg_ov_diversity = (n_ov_res_membership / n_ov_res 
            if n_ov_res > 0 else float('nan'))
    print('Ov. density\t= {:.6f}'.format(ov_density))
    print('Ov. diversity\t= {:.6f}'.format(avg_ov_diversity))
    measure_values.append(ov_density)
    measure_values.append(avg_ov_diversity)

    print('-' * 80)
    print(','.join(str(x) for x in measure_values))
    '''

    # save the mined organizational model to a file
    with open(fnout_org_model, 'w', encoding='utf-8') as fout:
        om.to_file_csv(fout)
    print('\n[Organizational model of {} resources in {} groups exported to "{}"]'
        .format(len(om.resources), om.group_number, fnout_org_model))

