#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('fn_event_log', 
    help='Path to input log file')
parser.add_argument('fn_co_mappings',
    help='Path to a file of input execution context mappings')
parser.add_argument('fn_org_model', 
    help='Path to input model file')

args = parser.parse_args()

fn_event_log = args.fn_event_log
fn_co_mappings = args.fn_co_mappings
fn_org_model = args.fn_org_model

if __name__ == '__main__':
    # read event log as input
    from ordinor.io import read_xes
    el = read_xes(fn_event_log)

    # read execution context mappings as input
    from ordinor.execution_context.base import BaseMiner
    with open(fn_co_mappings, 'rb') as f:
        ec_miner = BaseMiner.from_file(f)

    rl = ec_miner.derive_resource_log(el)

    # read organizational model as input
    from ordinor.org_model_miner import OrganizationalModel
    with open(fn_org_model, 'r', encoding='utf-8') as f:
        om = OrganizationalModel.from_file_csv(f)

    # Model evaluation (Global conformance)
    from ordinor.conformance import fitness, precision
    print('-' * 80)
    fitness_score = fitness(rl, om)
    print('Fitness\t\t= {:.3f}'.format(fitness_score))
    print()
    precision_score = precision(rl, om)
    print('Precision\t= {:.3f}'.format(precision_score))
    print()
