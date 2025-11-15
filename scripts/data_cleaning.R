# libraries
library(jsonlite)
library(tidyverse)
library(purrr)
library(arrow)

# dataset 5 --> extract json components
raw <- fromJSON("data/raw/dataset0005.json", simplifyVector = FALSE)

names(raw)

vorlagen <- raw$schweiz$vorlagen
length(vorlagen)

v1 <- vorlagen[[1]]
names(v1)

# dataset 9 --> transform parquet to csv for analysis
ds9 <- read_parquet("data/restricted/dataset0009.parquet")

# dataset 10 --> extract json L components
ds10 <- stream_in(file("data/raw/dataset0010.jsonl"), verbose = FALSE)