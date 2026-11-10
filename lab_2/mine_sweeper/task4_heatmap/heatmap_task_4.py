"""Create a dependency-free SVG heatmap for a Minesweeper game state.

The colours show P(mine): green is low risk, yellow is uncertain, and red is
high risk. Hidden cells outside the clue frontier are gray. This file is a
presentation helper; the submitted solver itself uses only standard-library
code and contains no plotting imports.

From this directory, run ``python heatmap_task_4.py state.txt``.
"""

import argparse
import html
import sys
import webbrowser
from pathlib import Path

# The example folder is a child of mine_sweeper; add its parent so this script
# can be started directly without installing the project as a package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from minesweeper_solver import mine_probability, parse_board


CELL_SIZE = 56
LEGEND_HEIGHT = 58
OUTPUT_FOLDER = Path(__file__).with_name("output")


def _is_probability_token(cell: str) -> bool:
    """Recognize the two-decimal tokens returned by mine_probability."""
    if "." not in cell:
        return False
    try:
        value = float(cell)
    except ValueError:
        return False
    return 0.0 <= value <= 1.0


def _risk_colour(probability: float) -> str:
    """Map probability 0..1 onto a green-to-yellow-to-red colour ramp."""
    green = (60, 190, 70)
    yellow = (255, 210, 70)
    red = (224, 40, 45)

    # Blend green to yellow below 50%, then yellow to red above 50%.
    if probability <= 0.5:
        start_colour = green
        end_colour = yellow
        blend_amount = probability / 0.5
    else:
        start_colour = yellow
        end_colour = red
        blend_amount = (probability - 0.5) / 0.5

    channels = []
    for start_value, end_value in zip(start_colour, end_colour):
        channel = round(start_value + (end_value - start_value) * blend_amount)
        channels.append(channel)
    return "#%02x%02x%02x" % tuple(channels)


def create_heatmap(state: str, output_path: Path) -> str:
    """Compute frontier probabilities, write their SVG heatmap, and return the board.

    Revealed clues use a light background, unconstrained hidden cells are gray,
    and probability cells receive both the risk colour and their numeric value.
    """
    probability_board = mine_probability(state)
    grid = parse_board(probability_board)
    rows = len(grid)
    columns = len(grid[0])
    image_width = columns * CELL_SIZE
    image_height = rows * CELL_SIZE + LEGEND_HEIGHT

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{image_width}" '
        f'height="{image_height}" viewBox="0 0 {image_width} {image_height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<g font-family="Arial, sans-serif" text-anchor="middle">',
    ]

    for row_index, row in enumerate(grid):
        for column_index, token in enumerate(row):
            x = column_index * CELL_SIZE
            y = row_index * CELL_SIZE

            # Separate probability tokens from clues and unrevealed cells so
            # the same display colour always has the same meaning.
            if _is_probability_token(token):
                fill_colour = _risk_colour(float(token))
                label = token
                label_colour = "#202124"
            elif token == "X":
                fill_colour = "#9aa0a6"
                label = "X"
                label_colour = "#202124"
            elif token == "M":
                fill_colour = "#e0282d"
                label = "M"
                label_colour = "#202124"
            else:
                fill_colour = "#f1f3f4"
                label = "" if token == "." else token
                label_colour = "#202124"

            svg_lines.append(
                f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" '
                f'height="{CELL_SIZE}" fill="{fill_colour}" stroke="#555"/>'
            )
            if label:
                svg_lines.append(
                    f'<text x="{x + CELL_SIZE / 2}" y="{y + CELL_SIZE / 2 + 6}" '
                    f'font-size="{14 if _is_probability_token(token) else 20}" '
                    f'fill="{label_colour}">{html.escape(label)}</text>'
                )

    # The legend explains how the cell fill maps to the probability of a mine.
    legend_y = rows * CELL_SIZE + 17
    legend_x = 12
    legend_width = max(image_width - 24, 120)
    gradient_id = "mine-risk-gradient"
    svg_lines.extend([
        f'<defs><linearGradient id="{gradient_id}">',
        '<stop offset="0%" stop-color="#3cbe46"/>',
        '<stop offset="50%" stop-color="#ffd246"/>',
        '<stop offset="100%" stop-color="#e0282d"/>',
        '</linearGradient></defs>',
        f'<rect x="{legend_x}" y="{legend_y}" width="{legend_width}" '
        f'height="14" fill="url(#{gradient_id})" stroke="#555"/>',
        f'<text x="{legend_x}" y="{legend_y + 32}" text-anchor="start" '
        'font-family="Arial, sans-serif" font-size="13">0.00 (safer)</text>',
        f'<text x="{image_width / 2}" y="{legend_y + 32}" '
        'font-family="Arial, sans-serif" font-size="13">P(mine)</text>',
        f'<text x="{image_width - legend_x}" y="{legend_y + 32}" '
        'text-anchor="end" font-family="Arial, sans-serif" font-size="13">1.00 (mine)</text>',
        '</g>',
        '</svg>',
    ])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(svg_lines), encoding="utf-8")
    return probability_board


def display_heatmap(output_path: Path) -> bool:
    """Open a generated SVG in the user's default web browser."""
    # A browser can display SVG directly, so this does not need an image or
    # plotting dependency. Use an absolute file URL for reliable Windows paths.
    return webbrowser.open_new_tab(output_path.resolve().as_uri())


def main() -> None:
    """Read a text game state and write an SVG probability heatmap."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state_file", type=Path, help="text file containing a space-separated game state")
    parser.add_argument(
        "--output",
        type=Path,
        help="optional SVG destination (default: output/<input-name>_heatmap.svg)",
    )
    args = parser.parse_args()

    state = args.state_file.read_text(encoding="utf-8")
    output_name = f"{args.state_file.stem}_heatmap.svg"
    output_path = args.output or OUTPUT_FOLDER / output_name
    probability_board = create_heatmap(state, output_path)

    print("Game state with frontier mine probabilities:")
    print(probability_board)
    print(f"\nHeatmap written to: {output_path}")


if __name__ == "__main__":
    main()
