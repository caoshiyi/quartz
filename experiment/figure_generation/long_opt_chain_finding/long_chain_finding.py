import pickle
import random
import json
import os

import quartz


class Query:
    def __init__(self):
        self.parent_hash = None
        self.cur_hash = None
        self.graph = None


def analyze_circuit(rank, qasm_str, max_depth):
    """
    Find the minimal number of steps needed to achieve a gate reduction from given circuit.
    Implemented by BFS.
    return: -1 if not found under max_depth, min #xfer o.w.
    """
    # prepare quartz context
    quartz_context = quartz.QuartzContext(gate_set=['h', 'cx', 't', 'tdg'],
                                          filename="../bfs_verified_simplified.json",
                                          no_increase=True, include_nop=False)
    qasm_parser = quartz.PyQASMParser(context=quartz_context)
    dag = qasm_parser.load_qasm_str(qasm_str=qasm_str)
    initial_graph = quartz.PyGraph(context=quartz_context, dag=dag)
    initial_graph_hash = initial_graph.hash()
    initial_graph_gate_count = initial_graph.gate_count
    print(f"[Rank {rank}] New circuit {initial_graph_hash} with {initial_graph_gate_count} gates.")

    # start BFS search for circuits with fewer gates
    candidate_queue = [[initial_graph, initial_graph_hash]]
    visited_hash_set = {initial_graph_hash: 0}
    searched_count = 0
    while len(candidate_queue) > 0:
        # get graph for current loop
        graph_packet = candidate_queue.pop(0)
        cur_graph = graph_packet[0]
        cur_graph_hash = graph_packet[1]
        all_nodes = cur_graph.all_nodes()

        # apply xfers to get to new graphs
        for i in range(len(all_nodes)):
            node = all_nodes[i]
            applicable_xfers = cur_graph.available_xfers_parallel(context=quartz_context,
                                                                  node=node)
            for xfer in applicable_xfers:
                new_graph = cur_graph.apply_xfer(xfer=quartz_context.get_xfer_from_id(id=xfer), node=node)
                new_hash = new_graph.hash()
                new_cnt = new_graph.gate_count
                # if new circuit has fewer gates, then we are done
                if new_cnt < initial_graph_gate_count:
                    final_depth = visited_hash_set[cur_graph_hash] + 1
                    return final_depth
                # otherwise we will continue search
                if new_hash not in visited_hash_set:
                    visited_hash_set[new_hash] = visited_hash_set[cur_graph_hash] + 1
                    candidate_queue.append([new_graph, new_hash])
                # and stop when we reach max depth
                if visited_hash_set[new_hash] > max_depth:
                    return -1
                # this is for logging
                searched_count += 1
                if searched_count % 1000 == 0:
                    print(f"[Rank {rank}] Searched {searched_count} circuits,"
                          f" now at depth {visited_hash_set[new_hash]}.")
    assert False


def main():
    # extract from result a circuit for each #min xfer
    circuit_idx = {}
    for idx in range(80):
        with open(f"./tmp/{idx}.tmp", 'rb') as handle:
            result_list = pickle.load(file=handle)
            for i in range(len(result_list)):
                result = result_list[i]
                if result not in circuit_idx:
                    circuit_idx[result] = i + idx * 125
    print(f"Circuit idx: {circuit_idx}")

    # extract those circuits
    random.seed(12345)
    circuit_dict_path = "../data/900000_graph.json"
    total_circuit_count = 10000
    max_search_depth = 8
    with open(circuit_dict_path, 'r') as handle:
        circuit_dict = json.load(handle)
    selected_hash_list = random.sample(list(circuit_dict), total_circuit_count)
    selected_circuit_list = []
    for selected_hash in selected_hash_list:
        selected_circuit_list.append(circuit_dict[selected_hash])
    # collect those we need
    final_circuit_dict = {}
    for steps in circuit_idx:
        index = circuit_idx[steps]
        final_circuit_dict[steps] = selected_circuit_list[index]

    # check those circuits
    output_path = "output"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for idx in final_circuit_dict:
        # check
        qasm_str = final_circuit_dict[idx][0]
        gate_count = final_circuit_dict[idx][1]
        print(f"Verifying circuit with min #xfer={idx}, it has {gate_count} gates.")
        verified_step_count = analyze_circuit(rank=0, qasm_str=qasm_str, max_depth=max_search_depth)
        assert verified_step_count == idx
        # save
        with open(f"./output/step{idx}.qasm", 'w') as handle:
            handle.write(final_circuit_dict[idx][0])


if __name__ == '__main__':
    main()