import os; os.system('clear')
import pandas as pd
import argparse
import numpy as np
from matplotlib import pyplot as plt
from ciervo.plots import emg_plot
from ciervo.io import example_marcha_larga, example_marcha



def main():
    parser = argparse.ArgumentParser(description='Fix BioRadio CSV file')
    parser.add_argument('--input', '-i', type=str, help='Input CSV file')
    # bool
    parser.add_argument('--bad_decimal', action='store_true', help='Se usa si el csv tiene decimales con coma')
    args = parser.parse_args()


    if args.bad_decimal:
        with open(args.input, 'r') as f:
            lines = f.readlines()
            columns = lines[0].split(',')
            # remove from columns ,'BioRadio Event', '\n'
            print(columns)
            columns = columns[:-2]
            data = []
            bad_count = 0
            for line in lines[1:]:
                split_line = line.split(',')
                #print(split_line)
                #print(len(split_line))
                row = [split_line[0]]
                for i in range(1, len(split_line) -2, 2):
                    try:
                        v = float('.'.join(split_line[i:i+2]))
                        row.append(float('.'.join(split_line[i:i+2])))
                    except:
                        bad_count += 1
                        pass

                data.append(row)
            df = pd.DataFrame(data, columns=columns)
            print(df.head())
            # Percentaje of bad values
            print(f'Bad values: {bad_count/len(data)*100:.2f}%')


    else:
        df = pd.read_csv(args.input, sep=',', decimal='.')
        #df = df.drop(columns=['BioRadio Event', 'Unnamed: 13'])



    # rename columns
    df = df.rename(columns={
    'Grip Strength Gionomet': 'Angle',
    'Flexlsq': 'EMG_Isquio',
    'ExtCuad': 'EMG_Cuadriceps',
    'Aductor': 'EMG_AductorLargo',
    'AbdGluM': 'EMG_GLMedio'
    })
    
    # convertir Angulo a grados
    df['Angle'] = 0.5107* df['Angle'] -216.03  # Convert to degrees

    # Convert formato de tiempo a segundos
    df['Elapsed Time'] = np.linspace(0, len(df['Elapsed Time'])/250, len(df['Elapsed Time']))
    print("Total duration in minutes: ", len(df['Elapsed Time'])/(60*250))

    # Todo a float
    df = df.astype(float)

    # Asign nan to values above threshold
    df = df.mask(df > 1000)

    # interpolate nan values
    df = df.interpolate()



if __name__ == '__main__':
    main()
    

