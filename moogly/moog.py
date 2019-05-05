import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os


class MOOG:
    MODES = ('synth', 'ew')
    def __init__(self, verbose=False, mode='synth', *args, **kwargs):
        self.verbose = verbose
        if mode.lower() not in MOOG.MODES:
            raise ValueError('mode has to be one of:', MOOG.MODES)
        self.mode = mode.lower()
        self.kwargs = kwargs
        if self.mode == 'ew':
            self.driver = 'abfind'
            self.kwargs['plot'] = 0
        elif self.mode == 'synth':
            self.driver = 'synth'
            self.kwargs['plot'] = 2

        self._create_config()
        self._run()

    def _create_config(self):
        fout = '{}\n'.format(self.driver)
        fout += "terminal     {}\n".format(self.kwargs.get('terminal', 'x11'))
        fout += "atmosphere   {}\n".format(self.kwargs.get('atmosphere', '1'))
        fout += "molecules    {}\n".format(self.kwargs.get('molecules', '2'))
        fout += "trudamp      {}\n".format(self.kwargs.get('trudamp', '1'))
        fout += "lines        {}\n".format(self.kwargs.get('lines', '1'))
        fout += "flux/int     {}\n".format(self.kwargs.get('fluxint', '0'))
        fout += "damping      {}\n".format(self.kwargs.get('damping', '0'))
        fout += "plot         {}\n".format(self.kwargs.get('plot'))
        fout += "units        {}\n".format(self.kwargs.get('units', '0'))
        fout += "model_in     {}\n".format(self.kwargs.get('model_in', 'atm.mod'))
        fout += "lines_in     {}\n".format(self.kwargs.get('lines_in', 'lines.moog'))
        fout += "summary_out  {}\n".format(self.kwargs.get('summary_out', 'summary.out'))
        fout += "standard_out {}\n".format(self.kwargs.get('standard_out', 'standard.out'))
        if self.mode == 'synth':
            fout += "synlimits\n{}\n".format(self.kwargs.get('synlimits', '5000.0 5050.0 0.01 1.'))
            fout += "obspectrum   {}\n".format(self.kwargs.get('obspectrum', '5'))
            fout += "plotpars     {}\n".format(self.kwargs.get('plotpars', '1'))
            fout += "{}\n".format(self.kwargs.get('plotpars1', '5000.0 5050.0  0.00 1.02'))
            fout += "{}\n".format(self.kwargs.get('plotpars2', '    0  0.00    0.00 0.00'))
            fout += "{}\n".format(self.kwargs.get('plotpars3', '  r 0.0209  1.7  0.40  2.2  0.0'))
            fout += "histogram    {}\n".format(self.kwargs.get('histogram', '1'))
            fout += "smoothed_out {}\n".format(self.kwargs.get('smoothed_out', 'synth.asc'))
            fout += "observed_in  {}\n".format(self.kwargs.get('observed_in', 'observed.asc'))
            fout += "abundances   {}\n".format(self.kwargs.get('abundances', '1 3'))
            fout += "   {}\n".format(self.kwargs.get('abundances1', '26   0.20   0.00   -0.20'))
        else:
            fout += "strong      {}\n".format(self.kwargs.get('strong', '0'))
            fout += "iraf        {}\n".format(self.kwargs.get('iraf', '0'))
            fout += "opacit      {}\n".format(self.kwargs.get('opacit', '0'))
            fout += "freeform    {}\n".format(self.kwargs.get('freeform', '0'))
            fout += "obspectrum   {}\n".format(self.kwargs.get('obspectrum', '0'))

        with open('conf.par', 'w') as f:
            f.write(fout)

    def _run(self):
        if self.verbose:
            print('Running MOOG...')
        if self.mode == 'synth':
            with open('tmp.synth', 'w') as f:
                f.write('conf.par\nq\n')
            os.system('MOOGSILENT < tmp.synth > /dev/null')
            os.system('rm -f tmp.synth')
        elif self.mode == 'ew':
            os.system('MOOGSILENT > /dev/null')
        if self.verbose:
            print('Done!')

    @property
    def output(self):
        if self.mode == 'synth':
            return MOOGSynthOutput(self.kwargs.get('output', 'synth.asc'))
        elif self.mode == 'ew':
            return MOOGEWOutput(self.kwargs.get('summary_out', 'summary.out'))


class MOOGSynthOutput:
    def __init__(self, fname):
        self.fname = fname
        self.data = self._read_output()
        self.wavelength = self.data[0][:, 0]
        self.flux = []
        for fl in self.data:
            self.flux.append(fl[:, 1])

    def _read_output(self):
        d = []
        data = []
        with open(self.fname, 'r') as lines:
            for i, line in enumerate(lines):
                if line.lstrip()[0].isalpha():
                    if len(d):
                        data.append(np.array(d))
                        d = []
                    continue
                d.append(list(map(float, filter(None, line.strip().split(' ')))))
            data.append(np.array(d))
        return data

    def plot(self, labels=None, *args, **kwargs):
        """Plot the synthetic spectrum/spectra
        Input
        -----
        labels : list
            Same length as the amount of spectra with label. Default is None
        args/kwargs
            Arguments as accepted by matplotlib
        """
        if labels is not None:
            for label, fl in zip(labels, self.flux):
                plt.plot(self.wavelength, fl, label=label, *args, **kwargs)
                plt.legend(loc='best', frameon=False)
        else:
            for fl in self.flux:
                plt.plot(self.wavelength, fl, *args, **kwargs)
        plt.xlabel('Wavelength')
        plt.ylabel('Flux')
        plt.show()


class MOOGEWOutput:
    def __init__(self, fname):
        self.fname = fname
        self.data = pd.read_csv(self.fname, sep=r'\s+', skiprows=5, skipfooter=4, engine='python')
    
    def __len__(self):
        return len(self.data)


if __name__ == "__main__":
    options = {'synlimits': '15547.4 15553.4 0.01 1.',
               'plotpars1': '15547.4 15553.4 0.00 1.02'
    }
    m = MOOG(mode='synth', verbose=True, **options)
    d = m.output
    d.plot(labels=map(lambda s: '[Fe/H]={}'.format(s),['0.20', '0.00', '-0.20']))
