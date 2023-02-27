import click
from src.planegame import FlightGame
from src.agent import train

@click.command()
@click.option('--play', is_flag=True, help="Play the game by yourself")
@click.option('--training', is_flag=True, help="Run a training session")
@click.option('--radar', is_flag=True, help="Show radar around the plane")
def run(play, training, radar):
    """Play flight game or train a neural network that will 
    learn how to avoid obstacles (rockets) and collect as many 
    points as possible.
    
    Run training example:
    python3 main.py --train 
    
    Play game by yourself example:
    python3 main.py --play
    """
    if play:
        game = FlightGame()
        game.run(radar)
    elif training:
        train()

if __name__ == "__main__":
    run()