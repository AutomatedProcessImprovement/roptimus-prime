import click

from pathlib import Path

from main import run_optimization


@click.group()
def cli():
    pass


@cli.command()
@click.option('--bpmn_path', required=True,
              help='Path to the BPMN model with the process model')
@click.option('--sim_params_path', required=True,
              help='Path to the JSON file with the simulation parameters')
@click.option('--constraints_path', required=True,
              help='Path to the JSON file with the resource constraints for the optimization')
@click.option('--total_iterations', required=True,
              help='Maximum number of iterations allowed')
@click.option('--algorithm', required=True,
              help='Algorithm to simulate [HC-STRICT / HC-FLEX]')
@click.option('--approach', required=False,
              help='OPTIONAL: Approach to simulate [CA / AR / CO / CAAR / ARCA / ALL]')
@click.pass_context
def start_optimization(ctx, bpmn_path, sim_params_path, constraints_path, total_iterations, algorithm, approach="ARCA"):
    run_optimization(bpmn_path, sim_params_path, constraints_path, total_iterations, algorithm, approach)


if __name__ == "__main__":
    cli()
