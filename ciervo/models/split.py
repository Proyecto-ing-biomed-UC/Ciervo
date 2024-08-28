from typing import Union
import pandas as pd
import numpy as np





def train_test_split(data: Union[list, pd.DataFrame], columna: list,  window_size=125, test_size=0.2, overlap=0,  random_state=None):
    """
    Splits the data into training and testing sets based on the specified window size and test size.
    Parameters:
    - data (Union[list, pd.DataFrame]): The data to be split. It can be either a list of dataframes or a single dataframe.
    - window_size (int): The size of each window for splitting the data. Default is 125.
    - test_size (float): The proportion of data to be allocated for testing. Default is 0.2.
    - random_state (int): The seed value for random number generation. Default is None.
    Returns:
    - train (numpy.ndarray): The training data. (N, window_size, columns)
    - test (numpy.ndarray): The testing data. (N, window_size, columns)
    """

    if random_state:
        np.random.seed(random_state)

    
    if isinstance(data, pd.DataFrame):
        data = [data]

    train_data = []
    train_label = []

    test_data = []
    test_label = []


    columna = [c.strip() for c in columna]

    for df_idx, df in enumerate(data):

        # check if columna is in df.columns
        column_is_present = True
        for c in columna:
            if c not in df.columns:
                print(f"El archivo id: {df_idx} no cuenta con la columna {c}. Archivo ignorado")
                column_is_present = False

        # Ignora archivo
        if not column_is_present:
            continue

        values = df[columna]
        label = df['labels']

        if overlap == 0:
            # non overlapping
            # number of windows
            n_windows = int(len(df)/window_size)

            # random indices
            indices = np.random.choice(range(n_windows), int(n_windows*test_size), replace=False)

            # split data
            for i in range(n_windows):
                if i in indices:
                    test_data.append(values.iloc[i*window_size:(i+1)*window_size])
                    test_label.append(label.iloc[(i+1)*window_size])
                else:
                    train_data.append(values.iloc[i*window_size:(i+1)*window_size])
                    train_label.append(label.iloc[(i+1)*window_size])

        else:
            # overlaping
            split_df = np.array_split(df, 20)

            # random indices
            test_indices = np.random.choice(range(len(split_df)), int(len(split_df)*test_size), replace=False)


            for s_idx, s_df in enumerate(split_df):
                n_windows = int((len(s_df)- window_size) // overlap)
                
                for i in range(n_windows):
                    if s_idx in test_indices:
                        test_data.append(values.iloc[i*overlap:(i+1)*overlap])
                        test_label.append(label.iloc[(i+1)*overlap])
                    else:
                        train_data.append(values.iloc[i*overlap:(i+1)*overlap])
                        train_label.append(label.iloc[(i+1)*overlap])


            

    train_data = np.array(train_data)
    train_label = np.array(train_label)

    test_data = np.array(test_data)
    test_label = np.array(test_label)

    
    return train_data, train_label, test_data, test_label



if __name__ == '__main__':
    import os; os.system('clear')

    from ciervo.io.load import example_marcha_larga

    data = example_marcha_larga()

    train,test = train_test_split(data, test_size=0.1, random_state=42)
    print(train.shape, test.shape)


    