
import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset


class PlantTraitsDataset(Dataset):
    def __init__(self, df, stage="train", transform=None, drop_outliers=False):
        self._base_init(df, drop_outliers)
        self.transform = transform

        # Add image paths to the DataFrame
        image_dir = f'data/raw/planttraits2024/{stage}_images/'
        self.df['image_paths'] = self.df['id'].apply(lambda x: image_dir+str(x)+'.jpeg')

        # Drop columns
        self.df = self.df.drop(columns = self.drop_cols, axis=1)

        # Split dataset into data, image paths and target columns to be used downstream
        self.data = self.df.drop(['image_paths'] + self.target_cols, axis=1)
        self.image_paths = self.df['image_paths']
        self.targets = self.df[self.target_cols]


    def __len__(self):
        return len(self.data)


    def __getitem__(self, idx):
        # Get image path and open the image
        img_path = self.image_paths.iloc[idx]
        img = Image.open(img_path).convert('RGB')

        # Apply transformations if provided
        if self.transform:
            img = self.transform(image = np.asarray(img))['image']

        # Get the corresponding row in the DataFrames
        targets = torch.tensor(self.targets.iloc[idx].values.astype(float), dtype=torch.float32)
        row = torch.tensor(self.data.iloc[idx].values.astype(float), dtype=torch.float32)

        return img, row, targets
    


    # ------- Private methods -------

    def _base_init(self, df, drop_outliers=False):
        self.df = df
        
        self.target_cols = ['X4_mean', 'X11_mean', 'X18_mean', 'X26_mean', 'X50_mean', 'X3112_mean']
        self.drop_cols = ['id', 'X4_sd', 'X11_sd', 'X18_sd', 'X26_sd', 'X50_sd', 'X3112_sd']

        if drop_outliers:
            self.df = self._drop_outliers(self.df)

    @staticmethod
    def _drop_outliers(df):
        df = df[(df['X4_mean'] <0.9206089075) &
                (df['X11_mean'] < 50.8005308717442) & 
                (df['X18_mean'] < 28.5236956466667) & 
                (df['X50_mean'] < 4.46409638322222) & 
                (df['X26_mean'] < 1395.93295633333) &                            
                (df['X3112_mean'] < 24518.4214958333
            )]
        return df