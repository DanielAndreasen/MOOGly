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
        fout = f'{self.driver}\n'
        fout += f"terminal     {self.kwargs.get('terminal', 'x11')}\n"
        fout += f"atmosphere   {self.kwargs.get('atmosphere', '1')}\n"
        fout += f"molecules    {self.kwargs.get('molecules', '2')}\n"
        fout += f"trudamp      {self.kwargs.get('trudamp', '1')}\n"
        fout += f"lines        {self.kwargs.get('lines', '1')}\n"
        fout += f"flux/int     {self.kwargs.get('fluxint', '0')}\n"
        fout += f"damping      {self.kwargs.get('damping', '0')}\n"
        fout += f"plot         {self.kwargs.get('plot')}\n"
        fout += f"units        {self.kwargs.get('units', '0')}\n"
        fout += f"model_in     {self.kwargs.get('model_in', 'atm.mod')}\n"
        fout += f"lines_in     {self.kwargs.get('lines_in', 'lines.moog')}\n"
        fout += f"summary_out  {self.kwargs.get('summary_out', 'summary.out')}\n"
        fout += f"standard_out {self.kwargs.get('standard_out', 'standard.out')}\n"
        if self.mode == 'synth':
            fout += f"synlimits\n{self.kwargs.get('synlimits', '5000.0 5050.0 0.01 1.')}\n"
            fout += f"obspectrum   {self.kwargs.get('obspectrum', '5')}\n"
            fout += f"plotpars     {self.kwargs.get('plotpars', '1')}\n"
            fout += f"{self.kwargs.get('plotpars1', '5000.0 5050.0  0.00 1.02')}\n"
            fout += f"{self.kwargs.get('plotpars2', '    0  0.00    0.00 0.00')}\n"
            fout += f"{self.kwargs.get('plotpars3', '  r 0.0209  1.7  0.40  2.2  0.0')}\n"
            fout += f"histogram    {self.kwargs.get('histogram', '1')}\n"
            fout += f"smoothed_out {self.kwargs.get('smoothed_out', 'synth.asc')}\n"
            fout += f"observed_in  {self.kwargs.get('observed_in', 'observed.asc')}\n"
            fout += f"abundances   {self.kwargs.get('abundances', '1 3')}\n"
            fout += f"   {self.kwargs.get('abundances1', '26   0.20   0.00   -0.20')}\n"
        else:
            fout += f''

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
    d.plot(labels=map(lambda s: f'[Fe/H]={s}',['0.20', '0.00', '-0.20']))
