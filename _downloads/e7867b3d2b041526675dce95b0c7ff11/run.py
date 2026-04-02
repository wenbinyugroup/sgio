import sgio

# There are two ways to call functions to convert the data.

# Method 1: Use the `convert` function to do this in one step.

sgio.convert(
    'sg2_airfoil.inp',  # Name of the Abaqus inp file.
    'sg2_airfoil_2.sg',  # Name of the VABS file.
    'abaqus', # Format of the CS data converted from.
    'vabs', # Format of the CS data converted to.
    model_type='bm2', # Structural model: Timoshenko.
)


# Method 2: Use the `read` and `write` functions to do this in two steps.

# sg = sgio.read(
#     'sg2_airfoil.inp',  # Name of the SG file.
#     'abaqus', # Format of the SG data. See doc for more info.
#     model='bm2', # Structural model: Timoshenko.
# )

# sgio.write(
#     sg,  # SG data
#     'sg2_airfoil.sg',  # Name of the SG file.
#     'vabs', # Format of the SG data. See doc for more info.
# )


