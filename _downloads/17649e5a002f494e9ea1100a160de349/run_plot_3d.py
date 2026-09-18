"""Example: 3D Plot of Multiple Cross-Sections Along a Blade Span (HTML).

Reads a layout CSV listing (spanwise_location, section_name) pairs, loads
each section's VABS input (.sg) and analysis result (.sg.K), then renders
them as an interactive 3D plotly figure written to an HTML file. Open the
HTML in a browser to rotate / zoom / pan smoothly even for dense meshes.
"""
import logging
import webbrowser
from pathlib import Path

from sgio import plot_sg_3d_beam_plotly

logging.basicConfig(level=logging.INFO)

output_html = Path('blade_3d.html').resolve()

plot_sg_3d_beam_plotly(
    csv_file='blade.csv',
    section_dir='cs',
    input_format='vabs',
    model_type='BM2',
    aspect_mode='data',
    output_html=str(output_html),
    title='Blade cross-sections',
)

print(f'Wrote {output_html}')
webbrowser.open(output_html.as_uri())
