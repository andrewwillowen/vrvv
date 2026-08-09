"""
Module for parsing computational output files to obtain data for calculating numeric predictions.
"""
from vrVV.definitions.universal_parameters import SPEED_OF_LIGHT, H_NOT_BAR, H_BAR, AMU, BOHR
from pathlib import Path
import numpy as np


def cfour_parser(anharm_path: Path, zetas_path: Path, cubic_path: Path, didQ_path: Path):
    """
    Parses CFOUR output files from anharmonic VPT2 calculation to obtain desired computational data.

    :param anharm_path: Path to anharm.out file
    :param zetas_path: Path to corioliszeta file
    :param cubic_path: Path to cubic file
    :param didQ_path: Path to didQ file
    :return: Tuple of arrays for import into DataObject

    *Note*: The file parsing code was cannibalized from an old script.  The results are rearranged
    to be in the proper order for use in the DataObject.
    """
    if not all(isinstance(x, Path) for x in [anharm_path, zetas_path, cubic_path, didQ_path]):
        raise TypeError('Inputs must be pathlib.Path objects.')
    files_present = True
    error_str = 'Could not find files at:\n'
    for in_file in [anharm_path, didQ_path, zetas_path, cubic_path]:
        if not in_file.is_file():
            files_present = False
            error_str += '{}\n'.format(in_file)
    if not files_present:
        raise FileNotFoundError(error_str)

    # parsing anharm.out
    with open(anharm_path, 'r') as anharm_in_raw:
        anharm_in = anharm_in_raw.read()

    try:
        rot_in = anharm_in.split('Be, B0 AND B-B0 SHIFTS FOR SINGLY EXCITED VIBRATIONAL STATES (MHz)')[1].split(
            'Vibrationally averaged dipole moment')[0].split('\n')[3].split()[1:]
        rot_formed = [float(x) for x in rot_in]
        vib_in = anharm_in.split('HARMONIC AND FUNDAMENTAL FREQUENCIES (cm-1) AND INTENSITIES (km/mol)')[-1].split(
            'ZERO-POINT VIBRATIONAL ENERGIES')[0].split('\n')[5:-3]
        # first 6 "vibrations" in CFOUR are the rotation and translations with frequencies of 0. Using dummy energies
        # for those.
        fun_vibs_formed = [1000000.0] * 6
        fun_vibs_formed.extend([float(vibration.split()[1]) for vibration in vib_in])
        n_modes = len(fun_vibs_formed)
    except IndexError:
        raise ValueError('Unable to parse the anharm.out file located at {}'.format(anharm_path))

    # parsing corioliszeta
    with open(zetas_path, 'r') as zetas_in_raw:
        zetas_in = zetas_in_raw.read().split('Coriolis')

    try:
        x_zetas_in = zetas_in[1].split('\n')[1:-1]
        y_zetas_in = zetas_in[2].split('\n')[1:-1]
        z_zetas_in = zetas_in[3].split('\n')[1:-1]
        x_zetas = [[[int(x.split()[0]) - 1, int(x.split()[1]) - 1], float(x.split()[2])] for x in x_zetas_in]
        y_zetas = [[[int(x.split()[0]) - 1, int(x.split()[1]) - 1], float(x.split()[2])] for x in y_zetas_in]
        z_zetas = [[[int(x.split()[0]) - 1, int(x.split()[1]) - 1], float(x.split()[2])] for x in z_zetas_in]
        # Starting with null data array of proper size
        x_zetas_out = [[0 for x in range(0, n_modes)] for y in range(0, n_modes)]
        y_zetas_out = [[0 for x in range(0, n_modes)] for y in range(0, n_modes)]
        z_zetas_out = [[0 for x in range(0, n_modes)] for y in range(0, n_modes)]
        for x in range(0, len(x_zetas)):
            x_zetas_out[x_zetas[x][0][0]][x_zetas[x][0][1]] = x_zetas[x][1]
            x_zetas_out[x_zetas[x][0][1]][x_zetas[x][0][0]] = x_zetas[x][1] * (-1)
        for x in range(0, len(y_zetas)):
            y_zetas_out[y_zetas[x][0][0]][y_zetas[x][0][1]] = y_zetas[x][1]
            y_zetas_out[y_zetas[x][0][1]][y_zetas[x][0][0]] = y_zetas[x][1] * (-1)
        for x in range(0, len(z_zetas)):
            z_zetas_out[z_zetas[x][0][0]][z_zetas[x][0][1]] = z_zetas[x][1]
            z_zetas_out[z_zetas[x][0][1]][z_zetas[x][0][0]] = z_zetas[x][1] * (-1)
        zetas_formed = [x_zetas_out, y_zetas_out, z_zetas_out]
    except IndexError:
        raise ValueError('Unable to parse the cubic file located at {}'.format(zetas_path))

    # parsing cubic
    with open(cubic_path, 'r') as cubic_raw_in:
        cubic_in = cubic_raw_in.read().split('\n')

    try:
        cubic = [[[int(x.split()[0]) - 1, int(x.split()[1]) - 1, int(x.split()[2]) - 1], float(x.split()[3])]
                 for x in cubic_in if x != '']
        # Starting with null data array of proper size
        cubic_out = [[[0 for x in range(0, n_modes)] for y in range(0, n_modes)] for z in range(0, n_modes)]
        for x in range(0, len(cubic)):
            cubic_out[cubic[x][0][0]][cubic[x][0][1]][cubic[x][0][2]] = cubic[x][1]
            cubic_out[cubic[x][0][0]][cubic[x][0][2]][cubic[x][0][1]] = cubic[x][1]
            cubic_out[cubic[x][0][1]][cubic[x][0][0]][cubic[x][0][2]] = cubic[x][1]
            cubic_out[cubic[x][0][1]][cubic[x][0][2]][cubic[x][0][0]] = cubic[x][1]
            cubic_out[cubic[x][0][2]][cubic[x][0][0]][cubic[x][0][1]] = cubic[x][1]
            cubic_out[cubic[x][0][2]][cubic[x][0][1]][cubic[x][0][0]] = cubic[x][1]
        cubic_fc_formed = cubic_out
    except IndexError:
        raise ValueError('Unable to parse the cubic file located at {}'.format(cubic_path))

    # parsing didQ
    with open(didQ_path, 'r') as didQ_in_raw:
        didQ_in = didQ_in_raw.read().split('\n')

    try:
        didQ = [[[int(didQ_in[x].split()[0]) - 1, int(didQ_in[x].split()[1]) - 1, int(didQ_in[x].split()[2]) - 1],
                 float(didQ_in[x].split()[3])] for x in range(0, len(didQ_in)) if didQ_in[x] != '']
        # Making full inertia derivatives data array
        didQ_out = [[[0 for x in range(0, 3)] for y in range(0, 3)] for z in range(0, n_modes)]
        for x in range(0, len(didQ)):
            didQ_out[didQ[x][0][2]][didQ[x][0][0]][didQ[x][0][1]] = didQ[x][1]
        inertia_der_formed = didQ_out
    except IndexError:
        raise ValueError('Unable to parse the didQ file located at {}'.format(didQ_path))

    starting_mode = 6  # CFOUR vibrational modes start at 6
    # n_modes is defined above
    W = [i for i in fun_vibs_formed]
    V = [i*(100/1)*SPEED_OF_LIGHT for i in fun_vibs_formed]
    zeta = [[[zetas_formed[rot_index][vib_index1][vib_index2]
              for rot_index in [0, 1, 2]]
             for vib_index2 in range(0, n_modes)]
            for vib_index1 in range(0, n_modes)]
    b_hz = [i*1000000 for i in rot_formed]
    b_cm = [i/(100*SPEED_OF_LIGHT) for i in rot_formed]
    k3 = [[[cubic_fc_formed[vib_index1][vib_index2][vib_index3]*100*SPEED_OF_LIGHT
            for vib_index3 in range(0, n_modes)]
           for vib_index2 in range(0, n_modes)]
          for vib_index1 in range(0, n_modes)]
    aD_conversion = AMU**(1/2) * BOHR
    # aD_conversion = (1.660529*10**(-27)/1)**(1/2)*(5.291*10**(-11))  # to kg**(1/2)*m from amu**(1/2)*Bohr
    aD = [[[inertia_der_formed[vib_index][rot_index1][rot_index2]*aD_conversion
            for rot_index2 in [0, 1, 2]]
           for rot_index1 in [0, 1, 2]]
          for vib_index in range(0, n_modes)]
    i0 = [H_NOT_BAR/(8*(np.pi**2)*b_hz[rot_index]) for rot_index in [0, 1, 2]]
    bvrr_constant = (-1)*(H_BAR**3)/(2*(H_NOT_BAR**(3/2)))
    bvrr = [[[(bvrr_constant
               * aD[vib_index][rot_index1][rot_index2]
               / (i0[rot_index1]*i0[rot_index2]*(V[vib_index]**(1/2))))
              for rot_index2 in [0, 1, 2]]
             for rot_index1 in [0, 1, 2]]
            for vib_index in range(0, n_modes)]
    data_arrays = (starting_mode, n_modes, W, V, zeta, b_cm, b_hz, k3, aD, i0, bvrr)
    return data_arrays


def gaussian_parser(file_path: Path):
    raise NotImplementedError


