from project.problem import Problem
import argparse

class AutomataProblem(Problem):
    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--check')

    def is_chosen_problem(self, args):
        return args.check is not None

    def run(self, args):
        # beolvassuk az input fajl tartalmat
        input_file = args.input

        with open(input_file, 'r') as f:
            data = f.read()

        # feldaraboljuk
        lines = data.splitlines()

        # kiolvasas a linesbol
        states = lines[0].split()
        # print(states)

        alphabet = lines[1].split()
        # print(alphabet)

        # nem kell split mert csak egy elemet olvasok ki
        initial_state = lines[2]  
        # print(initial_state)

        final_states = lines[3].split()
        # print(final_states)

        # a lista 4-es idnexu elemetol
        transition_lines = lines[4:]
        # print(transition_lines)

        # atmenet feldolgozasa
        transitions = {}
        for transition in transition_lines:
            parts = transition.split()

            source = parts[0]
            symbol = parts[1]
            destination = parts[2]

            transitions[(source, symbol)] = destination

        # print(transitions)  

        words = args.check.split(',')

        results = []

        for word in words:
            current_state = initial_state

            for symbol in word:
                if (current_state, symbol) in transitions:
                    current_state = transitions[(current_state, symbol)]
                else:
                    current_state = None
                    break

            if current_state in final_states:
                result = "IGEN"
            else:
                result = "NEM"

            results.append(result)

        output_file = args.output

        with open(output_file, 'w') as f:
            for result in results:
                f.write(result + '\n')