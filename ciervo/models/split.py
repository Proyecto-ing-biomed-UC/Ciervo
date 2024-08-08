from typing import Union
import pandas as pd
import numpy as np

def train_test_split(data: Union[list, pd.DataFrame], window_size=125, test_size=0.2, random_state=None):
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

    
    if isinstance(data, pd.DataFrame):
        data = [data]

    train = []
    test = []
    for df in data:
        # number of windows
        n_windows = int(len(df)/window_size)

        if random_state:
            np.random.seed(random_state)

        # random indices
        indices = np.random.choice(range(n_windows), int(n_windows*test_size), replace=False)

        # split data
        for i in range(n_windows):
            if i in indices:
                test.append(df.iloc[i*window_size:(i+1)*window_size])
            else:
                train.append(df.iloc[i*window_size:(i+1)*window_size])
    
    train = np.array(train)
    test = np.array(test)
    
    return train, test



if __name__ == '__main__':
    import os; os.system('clear')

    from ciervo.io.load import example_marcha_larga

    data = example_marcha_larga()

    train,test = train_test_split(data, test_size=0.1, random_state=42)
    print(train.shape, test.shape)


    