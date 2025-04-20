import pandas as pd

df=pd.read_parquet("D:\myprojects\Technocolabs\streamify\Streamify-RealTime-DataPipeline\docker\song-count.parquet", engine='pyarrow')
print(df.count())
print(df.head(5))