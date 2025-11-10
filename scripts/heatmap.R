library(ggplot2)
library(tidyverse)
library(pheatmap)

df <- data.frame(
  dataset = c("dataset0001", "dataset0002", "dataset0003", "dataset0004", "dataset0005"),
  valid_votes = c(1, 1, 1, 0, 1),
  registered_voters = c(1, 1, 0, 1, 0),
  invalid_votes = c(1, 0, 1, 1, 1),
  timestamp = c(0, 1, 1, 1, 0),
  region = c(1, 0, 1, 1, 0),
  candidate_name = c(1, 1, 1, 0, 0)
)

rownames(df) <- df$dataset
df$dataset <- NULL

palette <- colorRampPalette(c("#DCEEF9", "#0072B2"))(2)

pheatmap(
  as.matrix(df),
  color = palette,
  cluster_rows = F,
  cluster_cols = F,
  legend = F,
  main = "Presence of Attributes Across Datasets",
  angle_col = 45,
  fontsize = 11,
  border_color = "grey90"
)
