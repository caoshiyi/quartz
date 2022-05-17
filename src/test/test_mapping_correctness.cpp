#include "quartz/device/device.h"
#include "quartz/tasograph/tasograph.h"
#include "quartz/parser/qasm_parser.h"
#include "quartz/tasograph/substitution.h"
#include <iostream>

using namespace quartz;
using namespace std;

ostream &operator << ( ostream& stream, GateType t )
{
    const string name_list[] = {"h", "x", "y", "rx", "ry", "rz", "cx", "ccx", "add",
                                "neg", "z", "s", "sdg", "t", "tdg", "ch", "swap", "p",
                                "pdg", "rx1", "rx3", "u1", "u2", "u3", "ccz", "cz",
                                "input_qubit", "input_param"
    };
    return stream << name_list[int(t)];
}

int main() {
    // tof_3_after_heavy.qasm / t_cx_tdg.qasm
    string circuit_file_name = "../tof_3_after_heavy.qasm";
    cout << "This is test for init_physical_mapping on " << circuit_file_name <<".\n";

    // prepare context
    Context src_ctx({GateType::h, GateType::x, GateType::rz, GateType::add, GateType::swap,
                     GateType::cx, GateType::input_qubit, GateType::input_param, GateType::t, GateType::tdg});
    // parse qasm file
    QASMParser qasm_parser(&src_ctx);
    DAG *dag = nullptr;
    if (!qasm_parser.load_qasm(circuit_file_name, dag)) {
        cout << "Parser failed" << endl;
        return -1;
    }
    Graph graph(&src_ctx, dag);
    cout << "Circuit initialized\n";

    // print all Ops
    cout << "Out Edges" << endl;
    for (const auto& Op_edge : graph.outEdges) {
        cout << "Gate: " << Op_edge.first.guid << " has type " << Op_edge.first.ptr->tp << endl;
    }
    cout << "In Edges" << endl;
    for (const auto& Op_edge : graph.inEdges) {
        cout << "Gate: " << Op_edge.first.guid << " has type " << Op_edge.first.ptr->tp << endl;
    }
    cout << endl;

    // test init qubit mapping
    graph.init_physical_mapping(InitialMappingType::TRIVIAL, nullptr, -1, false, -1);
    cout << "Mapping has been initialized." << endl;
    MappingStatus succeeded = graph.check_mapping_correctness();
    if (succeeded == quartz::MappingStatus::VALID) std::cout << "Test has passed\n";
    else std::cout << "Test failed\n";
};
