import torchaudio
from torch.utils.data import Dataset
from torch import Tensor, FloatTensor
import os
import pandas as pd
from typing import Tuple
from torchaudio.transforms import Resample

class MillionSongDataset(Dataset):
    MULTI_LABEL = True
    NUM_LABELS = 50
    def __init__(self,
                 subset: str = 'train',
                 root: str="data/processed/msd/audio/",
                 meta_path: str="data/processed/MSD/", 
                 sample_rate: int=22050,
                 transforms=None,
                 **kwargs) -> None:
        self.root = root
        self.meta_path = meta_path
        self.subset = subset
        self.sample_rate = sample_rate
        self.transforms = transforms
        print(f"{self.meta_path} {self.subset}")
        self._get_song_list()

    def __getitem__(self, index) -> Tuple[Tensor, FloatTensor]:
        audio_path = os.path.join(self.root, self.fl[index])
        
        try:
            audio, sr = torchaudio.load(audio_path, format='mp3')
            if sr != self.sample_rate:
                transform = Resample(sr, self.sample_rate)
                audio = transform(audio)
            if audio.shape[-1] < 65024 + 1:
                raise Exception
        except Exception: 
            os.system(f"echo {self.fl[index]} >> data/processed/MSD/failed.txt")
            return self.__getitem__((index + 1) % len(self))
        
        
        audio = audio.mean(dim=0, keepdim=True)

        if self.transforms:
            audio = self.transforms(audio)
        return audio, FloatTensor(0)

    def _get_song_list(self):
        fl_path = os.path.join(self.meta_path, self.subset + '_filepaths.csv')
        df = pd.read_csv(fl_path)
        self.fl = df['0'].str[1:].values
    
    def __len__(self):
        return len(self.fl)
