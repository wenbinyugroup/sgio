# Convert cross-section data from Abaqus to VABS


Suppose a cross-section has been built in Abaqus and output to `sg2_airfoil.inp`.
This example shows how to convert the data to the VABS input (Timoshenko model) `sg2_airfoil.sg`:


## Running


There are two ways to do this: CLI and API.

Use CLI:

```bash
sgio convert sg2_airfoil.inp sg2_airfoil.sg -ff abaqus -ft vabs -m bm2
```

Use API:

```bash
python run.py
```
