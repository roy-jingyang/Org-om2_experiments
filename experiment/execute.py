#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This program delivers a batch evaluation script for experiments. It allows user
to configure the components to be included as the setup and then save the
setup. The program can then load the setup from the saved file, and starts to
instantiate all possible test instances following the setup and executes.

The underlying data structure of the setup is an unweighted acyclic directed
graph, where:
    * each node represents a step in the entire approach (usually, a method
    from a module should be invoked), and all the configuration and tag
    information related to the method used is stored as node attributes;
    * each node is described by a name specified by the user, and contains the
    following attributes:
        - 'label'
        - 'step'
        - 'invoke'
        - 'params'
        - (TBD, other attributes for nice visualization in Gephi)
    * each directed edge represents a possible combination of specific methods
    in the predecessor step and the successor step in the approach.

The setup (graph) is stored in GraphML format, which is XML-based and allows
node attributes as well as convenient visualization features.
"""

import sys

from os.path import join
from csv import writer

def _import_block(path_invoke):
    from importlib import import_module
    module = import_module('.'.join(path_invoke.split('.')[:-1]))
    foo = getattr(module, path_invoke.split('.')[-1])
    return foo

def execute(setup, seq_ix, exp_dirpath):
    sequence = list(setup.nodes[ix] for ix in seq_ix)

    # Step 0: input an event log
    step = 0
    reader = _import_block(sequence[step]['invoke'])
    params = sequence[step].get('params', None)
    if params is None:
        exit('[Node Error]\t"{}"'.format(sequence[step]['label']))
    else:
        params = eval(params)
    el = reader(params['filepath'])

    # determine execution contexts
    step += 1
    cls_ec_miner = _import_block(sequence[step]['invoke'])
    ec_miner_name = sequence[step]['label'].replace(' ', '')
    params = sequence[step].get('params', None)
    if params is None:
        ec_miner = cls_ec_miner(el)
    else:
        params = eval(params)
        ec_miner = cls_ec_miner(el, **params)
    rl = ec_miner.derive_resource_log(el)

    # characterize resources
    from ordinor.org_model_miner.resource_features import direct_count
    profiles = direct_count(rl)

    # discover resource grouping
    step += 1
    discoverer = _import_block(sequence[step]['invoke'])
    discoverer_name = sequence[step]['label'].replace(' ', '')
    params = sequence[step].get('params', None)
    if params is None:
        ogs = discoverer(profiles)
    else:
        params = eval(params)
        ogs = discoverer(profiles, **params)
    if type(ogs) is tuple:
        ogs = ogs[0]

    # profile resource groups
    step += 1
    assigner = _import_block(sequence[step]['invoke'])
    assigner_name = sequence[step]['label'].replace(' ', '')
    params = sequence[step].get('params', None)
    if params is None:
        om = assigner(ogs, rl)
    else:
        params = sequence[step].get('params', None)
        params = eval(params)
        om = assigner(ogs, rl, **params)

    # model evaluation
    from ordinor.conformance import fitness, precision
    fitness = fitness(rl, om)
    precision = precision(rl, om)

    k = om.group_number
    
    # export organizational models
    fnout = '{}-{}-{}.om'.format(
        ec_miner_name, discoverer_name, assigner_name)
    with open(join(exp_dirpath, fnout), 'w') as fout:
        om.to_file_csv(fout)

    return ('{}-{}-{}'.format(
        ec_miner_name, discoverer_name, assigner_name), 
        k, fitness, precision
    )

if __name__ == '__main__':
    fn_setup = sys.argv[1]
    dirout = sys.argv[2]
    path = sys.argv[3].split(',')

    from networkx import read_graphml
    setup = read_graphml(fn_setup)

    n_tests = 1
    name = ''

    l_test_results = list()

    for i in range(n_tests):
        result = list(execute(setup, path, dirout))
        name = result[0]
        l_test_results.append(result[1:])

    with open(join(dirout, '{}_report.csv'.format(name)), 'w+') as fout:
        writer = writer(fout)
        for i in range(n_tests):
            writer.writerow(
                [name] + 
                l_test_results[i]
            )
    
