# MOOGly

This is a wrapper around the spectroscopic software [MOOG](http://www.as.utexas.edu/~chris/moog.html).

# Install

```bash
pip install git+https://github.com/DanielAndreasen/MOOGly
```

# Usage
You simply have to specify the `mode` you want MOOG to run (either `ew` or `synth`).

```python
from moogly import MOOG

options = {'synlimits': '15547.4 15553.4 0.01 1.',
           'plotpars1': '15547.4 15553.4 0.00 1.02'}
m = MOOG(mode='synth', verbose=True, **options)
d = m.output
d.plot()
```

## `MOOG.output`
The property `output` returns the scientific output from the run with the `ew` mode
or the `synth` mode.

For the `synth` mode, there are the following attributes and methods:
* `wavelength`: Common wavelength for all the synthetic spectra
* `flux`: All the flux vectors for the different synthetic spectra
* `data`: A structure of `[[wavelength, flux1], [wavelength, flux2], ...]`
* `plot()`: A method to plot the synthetic spectra. Can also be used with labels parameter:
`plot(labels=['label1', 'label2', ...])`
This method can also be used with normal matplotlib arguments and keyword arguments

For the `ew` mode, there is the following attribute:
* `data`: This is a pandas dataframe made from the output at `summary_out` given in the MOOG configuration file
