
import pandas as pd
import lightning as L
import torch
from torch.utils.data import random_split, DataLoader
from torchvision import transforms
from pathlib import Path

from src.config.training_config import TrainingConfig
from src.data.plant_traits_dataset import PlantTraitsDataset
from src.data.transform_holder import TransformHolder

class PlantTraitsDataModule(L.LightningDataModule):
    def __init__(self, config: TrainingConfig):
        super().__init__()
        self.data_dir = config.data_dir
        self.batch_size = config.batch_size
        self.transform = TransformHolder.get_train_transform()

    def prepare_data(self):
        # Download, tokenize, preprocess, etc.
        pass

    def setup(self, stage: str):
        if stage == "fit":
            train_path = Path(self.data_dir) / Path("train.csv")
            train_df = pd.read_csv(train_path)
            plant_traits_full = PlantTraitsDataset(train_df, stage="train", transform=self.transform)
            self.plant_traits_train, self.plant_traits_val = random_split(
                plant_traits_full, [50489, 5000], generator=torch.Generator()
            )

        if stage == "test":
            test_path = Path(self.data_dir) / Path("test.csv")
            test_df = pd.read_csv(test_path)
            self.plant_traits_test = PlantTraitsDataset(test_df, stage="test")

        if stage == "predict":
            path = Path(self.data_dir) / Path("test.csv")
            df = pd.read_csv(path)
            self.plant_traits_predict = PlantTraitsDataset(df, stage="test")


    def train_dataloader(self):
        return DataLoader(self.plant_traits_train, batch_size=self.batch_size, shuffle=True)

    def val_dataloader(self):
        return DataLoader(self.plant_traits_val, batch_size=self.batch_size)

    def test_dataloader(self):
        return DataLoader(self.plant_traits_test, batch_size=self.batch_size)

    def predict_dataloader(self):
        return DataLoader(self.plant_traits_predict, batch_size=self.batch_size)
    

    # Transforms - if we start adding many, we can pull into a TransformHolder class
    @staticmethod
    def get_base_transform():
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])