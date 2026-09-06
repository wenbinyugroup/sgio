(guide_model)=
# Material and Structural Models

The `model_type` argument selects how a mesh is interpreted by the solver. Each
page below describes the kinematics and constitutive relation of one model.

```{toctree}
:hidden:

sd_cauchy
pl_kirchhoff
pl_reissner
bm_euler
bm_timoshenko
```

| Tag | Model | Kind |
|---|---|---|
| `SD1` | [](sd_cauchy.md) | solid |
| `PL1` | [](pl_kirchhoff.md) | plate / shell |
| `PL2` | [](pl_reissner.md) | plate / shell |
| `BM1` | [](bm_euler.md) | beam |
| `BM2` | [](bm_timoshenko.md) | beam |

Which formats accept which models is listed in {doc}`/ref/formats`.
