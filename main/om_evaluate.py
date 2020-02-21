#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('fn_event_log', 
    help='Path to input log file')
parser.add_argument('fn_mode_mappings',
    help='Path to a file to input execution mode mappings')
parser.add_argument('fn_org_model', 
    help='Path to input model file')

args = parser.parse_args()

fn_event_log = args.fn_event_log
fn_mode_mappings = args.fn_mode_mappings
fn_org_model = args.fn_org_model

def jaccard_index(set_a, set_b):
    return len(set.intersection(set_a, set_b)) / len(set.union(set_a, set_b))

if __name__ == '__main__':
    # read event log as input
    from orgminer.IO.reader import read_xes
    with open(fn_event_log, 'r', encoding='utf-8') as f:
        el = read_xes(f)

    # read execution mode mappings as input
    from orgminer.ExecutionModeMiner.base import BaseMiner
    with open(fn_mode_mappings, 'r') as f:
        exec_mode_miner = BaseMiner.from_file(f)

    rl = exec_mode_miner.derive_resource_log(el)

    # read organizational model as input
    from orgminer.OrganizationalModelMiner.base import OrganizationalModel
    with open(fn_org_model, 'r', encoding='utf-8') as f:
        om = OrganizationalModel.from_file_csv(f)

    # Evaluation
    # Global conformance measures
    from orgminer.Evaluation.l2m import conformance
    print('-' * 80)
    fitness_score = conformance.fitness(rl, om)
    print('Fitness\t\t= {:.3f}'.format(fitness_score))
    print()
    precision_score = conformance.precision(rl, om)
    print('Precision\t= {:.3f}'.format(precision_score))
    print()

    '''
    jac_resource_sets = jaccard_index(set(rl['resource']), set(om.resources))
    print('Jac. index (resources)\t= {:.3f}'.format(jac_resource_sets))
    print()
    jac_mode_sets = jaccard_index(
        set(rl[['case_type', 'activity_type', 'time_type']]
            .drop_duplicates().itertuples(index=False, name=None)),
        set(om.find_all_execution_modes()))
    print('Jac. index (modes)\t= {:.3f}'.format(jac_mode_sets))
    print()
    '''

