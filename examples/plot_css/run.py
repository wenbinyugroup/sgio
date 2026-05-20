import logging
import sgio

logging.basicConfig(level=logging.INFO)

sgio.merge_sections_from_csv(
    csv_file="blade.csv",
    section_dir="cs",
    input_format="gmsh",
    output_file="blade_merged.msh",
    output_format="gmsh22",
)
