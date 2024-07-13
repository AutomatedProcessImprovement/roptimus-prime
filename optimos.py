
from click.decorators import option, pass_context,group
from pareto_algorithms_and_metrics.main import run_optimization


@group()
def cli():
    pass


@cli.command()
@option('--bpmn_path', required=True,
              help='Path to the BPMN model with the process model')
@option('--sim_params_path', required=True,
              help='Path to the JSON file with the simulation parameters')
@option('--constraints_path', required=True,
              help='Path to the JSON file with the resource constraints for the optimization')
@option('--total_iterations', required=True,
              help='Maximum number of iterations allowed')
@option('--algorithm', required=True,
              help='Algorithm to simulate [HC-STRICT / HC-FLEX]')
@option('--approach', required=False, default="ARCA",
              help='OPTIONAL: Approach to simulate [CA / AR / CO / CAAR / ARCA / ALL]')
@pass_context
def start_optimization(ctx, bpmn_path, sim_params_path, constraints_path, total_iterations, algorithm, approach):
    run_optimization(bpmn_path, sim_params_path, constraints_path, total_iterations, algorithm, approach,"opti-output" , "DEFAULT")


if __name__ == "__main__":
    cli()
