#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

fn_event_log = sys.argv[1]
fnout_org_model = sys.argv[2]

if __name__ == '__main__':
    # read event log as input
    from orgminer.IO.reader import read_xes
    with open(fn_event_log, 'r', encoding='utf-8') as f:
        el = read_xes(f)

    # 1. Learn execution modes
    from orgminer.ExecutionModeMiner import direct_groupby, informed_groupby
    print('Input a number to choose a solution:')
    print('\t0. ATonly')
    #print('\t11. CTonly (requires specifying a case attribute)')
    #print('\t12. CT+AT (requires specifying a case attribute)')
    #print('\t13. AT+TT')
    print('\t1. CT+AT+TT (case attribute)')
    #print('\t14. CTonly (trace clustering)')
    print('\t2. CT+AT+TT (trace clustering)')
    mode_learning_option = int(input())

    if mode_learning_option in [11, 12, 13, 14]:
        raise NotImplementedError

    elif mode_learning_option == 0:
        exec_mode_miner = direct_groupby.ATonlyMiner(el)

    elif mode_learning_option == 1:
        print('\tSpecify the name of the case attribute:', end=' ')
        sp_case_attr_name = input()
        print('\tInput a number to choose a desired time unit:')
        units = ['hour', 'day', 'weekday']
        for i, unit in enumerate(units):
            print('\t\t{}. {}'.format(i, unit))
        sp_time_unit = input()
        exec_mode_miner = direct_groupby.FullMiner(el,
            case_attr_name=sp_case_attr_name,
            resolution=sp_time_unit)

    elif mode_learning_option == 11: # NOTE: temporarily disabled
        print('Specify the name of the case attribute:', end=' ')
        sp_case_attr_name = input()
        exec_mode_miner = direct_groupby.CTonlyMiner(el, 
            case_attr_name=sp_case_attr_name)
    elif mode_learning_option == 12: # NOTE: temporarily disabled
        print('Specify the name of the case attribute:', end=' ')
        sp_case_attr_name = input()
        exec_mode_miner = direct_groupby.ATCTMiner(el,
            case_attr_name=sp_case_attr_name)
    elif mode_learning_option == 13: # NOTE: temporarily disabled
        print('Input the desired datetime resolution:', end=' ')
        resolution = input()
        exec_mode_miner = direct_groupby.ATTTMiner(el, 
            resolution=resolution)
    elif mode_learning_option == 14: # NOTE: temporarily disabled
        print('Input the path of the partitioning file:', end=' ')
        fn_partition = input()
        exec_mode_miner = informed_groupby.TraceClusteringCTMiner(
            el, fn_partition=fn_partition)

    elif mode_learning_option == 2:
        print('Input the path of the partitioning file:', end=' ')
        fn_partition = input()
        print('\tInput a number to choose a desired time unit:')
        units = ['hour', 'day', 'weekday']
        for i, unit in enumerate(units):
            print('\t\t{}. {}'.format(i, unit))
        sp_time_unit = input()
        exec_mode_miner = informed_groupby.TraceClusteringFullMiner(el,
            fn_partition=fn_partition,
            resolution=sp_time_unit)
    else:
        raise ValueError('Option not recognized')

    # Derive resource log
    rl = exec_mode_miner.derive_resource_log(el)


    # 2. Discover organizational groups
    print('Input a number to choose a solution:')
    #print('\t10. Default Mining (Song)')
    #print('\t11. Metric based on Joint Activities/Cases (Song)')
    print('\t0. AHC: Hierarchical Organizational Mining (Song and van der Aalst, 2008)')
    #print('\t13. Overlapping Community Detection')
    #print('\t14. GMM: Gaussian Mixture Model')
    print('\t1. MOC: Model based Overlapping Clustering (Yang et al., 2018)')
    #print('\t16. Fuzzy c-means')
    mining_option = int(input())

    if mining_option in [10, 11, 13, 14, 16]:
        raise NotImplementedError

    elif mining_option == 10: #NOTE: temporarily disabled
        from orgminer.OrganizationalModelMiner.base import default_mining
        ogs = default_mining(rl)

    elif mining_option == 11: #NOTE: temporarily disabled
        print('Input desired range (e.g. [low, high)) of number of groups:',
            end=' ')
        num_groups = input()
        num_groups = num_groups[1:-1].split(',')
        num_groups = list(range(int(num_groups[0]), int(num_groups[1])))

        # select method (MJA/MJC)
        print('Input a number to choose a method:')
        print('\t0. MJA')
        print('\t1. MJC')
        print('Option: ', end='')
        method_option = int(input())
        if method_option == 0:
            # build profiles
            from orgminer.ResourceProfiler.raw_profiler import \
                count_execution_frequency
            profiles = count_execution_frequency(rl, scale='log')
            from orgminer.OrganizationalModelMiner.community.graph_partitioning\
                import mja
            print('Input a number to choose a metric:')
            metrics = ['euclidean', 'correlation']
            print('\t0. Distance (Euclidean)')
            print('\t1. PCC')
            print('Option: ', end='')
            metric_option = int(input())
            ogs = mja(profiles, num_groups, metric=metrics[metric_option])
        elif method_option == 1:
            from orgminer.OrganizationalModelMiner.community.graph_partitioning\
                import mjc
            ogs = mjc(el, num_groups)
        else:
            raise ValueError
    elif mining_option == 0:
        print('Input desired range (e.g. [low, high)) of number of groups:',
            end=' ')
        num_groups = input()
        num_groups = num_groups[1:-1].split(',')
        num_groups = list(range(int(num_groups[0]), int(num_groups[1])))

        # build profiles
        from orgminer.ResourceProfiler.raw_profiler import count_execution_frequency
        profiles = count_execution_frequency(rl, scale='log')
        from orgminer.OrganizationalModelMiner.clustering.hierarchical \
            import ahc
        ogs, og_hcy = ahc(profiles, num_groups, method='ward')

        #og_hcy.to_csv(fnout_org_model + '_hierarchy')

    elif mining_option == 13: #NOTE: temporarily disabled
        # build profiles
        from orgminer.ResourceProfiler.raw_profiler import count_execution_frequency
        profiles = count_execution_frequency(rl, scale='log')

        from orgminer.OrganizationalModelMiner.community import overlap
        print('Input a number to choose a method:')
        print('\t0. CFinder (Clique Percolation Method)') 
        print('\t1. LN + Louvain (Link partitioning)')
        print('\t2. OSLOM (Local expansion and optimization)')
        print('\t3. COPRA (Agent-based dynamical methods)')
        print('\t4. SLPA (Agent-based dynamical methods)')
        print('Option: ', end='')
        method_option = int(input())
        if method_option == 0:
            ogs = overlap.clique_percolation(
                profiles, metric='correlation')
        elif method_option == 1:
            print('Input the desired number of groups:', end=' ')
            num_groups = int(input())
            ogs = overlap.link_partitioning(
                profiles, num_groups, metric='correlation')
        elif method_option == 2:
            ogs = overlap.local_expansion(
                profiles, metric='correlation')
        elif method_option == 3:
            ogs = overlap.agent_copra(
                profiles, metric='correlation')
        elif method_option == 4:
            ogs = overlap.agent_slpa(
                profiles, metric='correlation')
        else:
            raise ValueError

    elif mining_option == 14: #NOTE: temporarily disabled
        print('Input desired range (e.g. [low, high)) of number of groups:',
            end=' ')
        num_groups = input()
        num_groups = num_groups[1:-1].split(',')
        num_groups = list(range(int(num_groups[0]), int(num_groups[1])))

        # build profiles
        from orgminer.ResourceProfiler.raw_profiler import count_execution_frequency
        profiles = count_execution_frequency(rl, scale='log')

        print('Input a threshold value [0, 1), in order to determine the ' +
            'resource membership:', end=' ')
        user_selected_threshold = input()
        user_selected_threshold = (float(user_selected_threshold)
            if user_selected_threshold != '' else None)

        from orgminer.OrganizationalModelMiner.clustering.overlap import gmm
        ogs = gmm(profiles, num_groups, 
            threshold=user_selected_threshold,
            init='kmeans')
    elif mining_option == 1:
        print('Input desired range (e.g. [low, high)) of number of groups:',
            end=' ')
        num_groups = input()
        num_groups = num_groups[1:-1].split(',')
        num_groups = list(range(int(num_groups[0]), int(num_groups[1])))

        # build profiles
        from orgminer.ResourceProfiler.raw_profiler import count_execution_frequency
        profiles = count_execution_frequency(rl, scale='log')

        from orgminer.OrganizationalModelMiner.clustering.overlap import moc
        ogs = moc(profiles, num_groups,
            init='kmeans')
    elif mining_option == 16: #NOTE: temporarily disabled
        print('Input desired range (e.g. [low, high)) of number of groups:',
            end=' ')
        num_groups = input()
        num_groups = num_groups[1:-1].split(',')
        num_groups = list(range(int(num_groups[0]), int(num_groups[1])))

        # build profiles
        from orgminer.ResourceProfiler.raw_profiler import count_execution_frequency
        profiles = count_execution_frequency(rl, scale='log')

        print('Input a threshold value [0, 1), in order to determine the ' +
                'resource membership (Enter to use a "null" threshold):',
                end=' ')
        user_selected_threshold = input()
        user_selected_threshold = (float(user_selected_threshold)
                if user_selected_threshold != '' else None)

        from orgminer.OrganizationalModelMiner.clustering.overlap import fcm
        ogs = fcm(profiles, num_groups, 
            threshold=user_selected_threshold,
            init='kmeans')

    else:
        raise Exception('Failed to recognize input option!')


    # 3. Assign execution modes to groups
    from orgminer.OrganizationalModelMiner.mode_assignment import \
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
    '''
    from orgminer.Evaluation.m2m.cluster_validation import silhouette_score
    from numpy import mean
    silhouette_score = mean(list(silhouette_score(ogs, profiles).values()))
    print('Silhouette\t= {:.6f}'.format(silhouette_score))
    print('-' * 80)
    print()
    '''
    
    from orgminer.Evaluation.l2m import conformance
    fitness_score = conformance.fitness(rl, om)
    print('Fitness\t\t= {:.3f}'.format(fitness_score))
    measure_values.append(fitness_score)
    print()
    precision_score = conformance.precision(rl, om)
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

