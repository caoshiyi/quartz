#include "device/device.h"
#include <iostream>

int main() {
    auto device_graph = quartz::DeviceTopologyGraph(9);
    device_graph.add_qubit();
    device_graph.add_edge(0, 1, 4);
    device_graph.add_edge(0, 7, 8);
    device_graph.add_edge(1, 2, 8);
    device_graph.add_edge(1, 7, 11);
    device_graph.add_edge(2, 3, 7);
    device_graph.add_qubit();
    device_graph.add_edge(2, 8, 2);
    device_graph.add_edge(2, 5, 4);
    device_graph.add_edge(3, 4, 9);
    device_graph.add_edge(3, 5, 14);
    device_graph.add_edge(4, 5, 10);
    device_graph.add_edge(5, 6, 2);
    device_graph.add_edge(6, 7, 1);
    device_graph.add_edge(6, 8, 6);
    device_graph.add_edge(7, 8, 7);
    device_graph.add_qubit();
    // device_graph.print();
    for (int i = 0; i < 12; ++i) {
        std::cout << "dst: " << i << ", cost: " << device_graph.cal_swap_cost(0, i) << '\n';
    }
};