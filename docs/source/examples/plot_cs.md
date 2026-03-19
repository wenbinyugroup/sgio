# Plot Cross-Section with Beam Properties

## Problem Description

This example demonstrates how to visualize a VABS cross-section geometry with beam properties overlay using SGIO.

## File List

- [plot_cs.py](../../../examples/plot_cs/plot_cs.py): Main Python script
- [sg21eb_tri3_vabs40.sg](../../../examples/plot_cs/sg21eb_tri3_vabs40.sg): VABS cross-section input file
- [sg21eb_tri3_vabs40.sg.K](../../../examples/plot_cs/sg21eb_tri3_vabs40.sg.K): VABS beam properties output


## How to Run

```bash
cd examples/plot_cs
python plot_cs.py
```


## Expected Outcome

The script displays a matplotlib window showing the cross-section geometry with:
- The mesh visualization
- Neutral axis
- Shear center
- Principal axes

```{figure} ../../../examples/plot_cs/sg21eb_tri3_vabs40.png
:align: center
```
