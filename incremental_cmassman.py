import csv
import time
import random
import matplotlib.pyplot as plt
import sys  # Import sys to stop the program

class IncrementalkSAT:
    def __init__(self, clauses):
        self.clauses = clauses
        self.num_vars = self.get_num_vars()

    def get_num_vars(self):
        """Get the number of variables from clauses."""
        return max(abs(lit) for clause in self.clauses for lit in clause)

    def is_satisfied(self, assignment):
        """Check if the current assignment satisfies the clauses."""
        for clause in self.clauses:
            if not any((lit > 0 and assignment[lit - 1]) or (lit < 0 and not assignment[abs(lit) - 1]) for lit in clause):
                return False
        return True

    def incremental_search(self):
        """Incrementally search for a satisfying assignment."""
        assignment = [None] * self.num_vars  # None means unassigned

        def backtrack(index):
            if index == self.num_vars:
                # If we've assigned all variables, check satisfaction
                return self.is_satisfied(assignment)

            # Try assigning True
            assignment[index] = True
            if backtrack(index + 1):
                return True

            # Try assigning False
            assignment[index] = False
            if backtrack(index + 1):
                return True

            # Reset assignment for backtracking
            assignment[index] = None
            return False

        if backtrack(0):
            return True  # Satisfiable
        else:
            return False


def parse_ksat_cnf(file_name):
    """Parse a CNF .csv file to retrieve clauses and satisfiability information."""
    problems = []
    with open(file_name, mode='r', encoding='utf-8-sig') as file:
        csv_reader = csv.reader(file)
        current_clauses = []
        satisfiability = None
        for row in csv_reader:
            # Clean up the row by removing empty elements
            row = [element for element in row if element]
            
            if len(row) == 0:
                continue  # Skip empty rows
            
            if row[0].startswith('c'):
                # Read the comment line to get satisfiability (U or S)
                satisfiability = row[3] if len(row) > 3 else None
            elif row[0].startswith('p'):
                # Read the problem line (p cnf <num_vars> <num_clauses>)
                num_vars = int(row[2])
                num_clauses = int(row[3])
                current_clauses = []
            else:
                # This is a clause line, add it to the current clauses
                clause = [int(lit) for lit in row if lit != '0']
                current_clauses.append(clause)

                # If we've collected all clauses, save the problem
                if len(current_clauses) == num_clauses:
                    problems.append({
                        'num_vars': num_vars,
                        'num_clauses': num_clauses,
                        'clauses': current_clauses,
                        'satisfiability': satisfiability
                    })
                    current_clauses = []  # Reset for the next problem
                    satisfiability = None  # Reset for the next problem

    return problems


def time_solver(clauses):
    """Time the k-SAT solver on a given set of clauses."""
    solver = IncrementalkSAT(clauses)

    start_time = time.time()
    satisfiable = solver.incremental_search()
    end_time = time.time()

    return end_time - start_time, satisfiable


def run_ksat_cases(file_name, output_file):
    """Run timing experiments for CNF files parsed with satisfiability information."""
    problems = parse_ksat_cnf(file_name)
    sizes = []
    times = []
    answers = []

    with open(output_file, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['Number of Variables', 'Number of Clauses', 'Time (seconds)', 'Satisfiable (Solver)', 'Expected'])

        for problem in problems:
            num_vars = problem['num_vars']
            num_clauses = problem['num_clauses']
            clauses = problem['clauses']
            satisfiability = problem['satisfiability']

            elapsed_time, solver_result = time_solver(clauses)
            sizes.append(num_vars)
            times.append(elapsed_time)
            answers.append(solver_result)

            # Prepare output line
            output_line = (f"Vars: {num_vars}, Clauses: {len(clauses)}, Time: {elapsed_time:.6f} seconds, "
                           f"Satisfiable (Solver): {solver_result}, Expected: {satisfiability}")
            print(output_line)
            
            # Also write the same output to the file
            csv_writer.writerow([num_vars, num_clauses, elapsed_time, solver_result, satisfiability])

            # Stop the program if the solver result does not match the expected satisfiability
            if (solver_result and satisfiability == 'U') or (not solver_result and satisfiability == 'S'):
                error_message = (f"Mismatch detected! Solver: {solver_result}, Expected: {satisfiability}")
                print(error_message)
                sys.exit("Stopping the program due to mismatched results.")

    return sizes, times, answers


def plot_results(sizes, times, answers):
    """Plot the results as a point graph with different colors for satisfiable and unsatisfiable results."""
    plt.figure(figsize=(10, 6))
    
    # Separate satisfiable and unsatisfiable results for different colors
    satisfiable_sizes = [size for size, answer in zip(sizes, answers) if answer]
    satisfiable_times = [time for time, answer in zip(times, answers) if answer]
    
    unsatisfiable_sizes = [size for size, answer in zip(sizes, answers) if not answer]
    unsatisfiable_times = [time for time, answer in zip(times, answers) if not answer]
    
    # Plot satisfiable results in blue
    plt.scatter(satisfiable_sizes, satisfiable_times, color='blue', marker='o', label='Satisfiable')

    # Plot unsatisfiable results in red
    plt.scatter(unsatisfiable_sizes, unsatisfiable_times, color='red', marker='x', label='Unsatisfiable')

    plt.title('incremental kSAT Solver Timing Results')
    plt.xlabel('Number of Variables')
    plt.ylabel('Time (seconds)')
    plt.grid(True)
    plt.legend(loc='upper left')
    plt.show()


if __name__ == "__main__":
    # Specify the CNF file to test
    TestFile = "kSAT_cmassman.csv"
    OutputFile = "outputfile_cmassman.csv"

    # Run the cases using the file parsed from the CNF file and save results to a CSV file
    sizes, times, answers = run_ksat_cases(TestFile, OutputFile)
    plot_results(sizes, times, answers)

