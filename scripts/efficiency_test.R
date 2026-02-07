library(ggplot2)

folder <- "transformations"

soc_files <- list.files(folder, pattern = "\\.soc$", full.names = TRUE)
ttl_files <- list.files(folder, pattern = "\\.ttl$", full.names = TRUE)

soc_stems <- tools::file_path_sans_ext(basename(soc_files))
ttl_stems <- tools::file_path_sans_ext(basename(ttl_files))

common_stems <- intersect(soc_stems, ttl_stems)

# Sanity check (mismatches)
soc_only <- setdiff(soc_stems, ttl_stems)
ttl_only <- setdiff(ttl_stems, soc_stems)

if (length(soc_only) > 0) {
  message("These have .soc but no matching .ttl: ", paste(soc_only, collapse = ", "))
}
if (length(ttl_only) > 0) {
  message("These have .ttl but no matching .soc: ", paste(ttl_only, collapse = ", "))
}
# Sanity check over

soc_map <- setNames(soc_files, soc_stems)
ttl_map <- setNames(ttl_files, ttl_stems)

soc_matched <- soc_map[common_stems]
ttl_matched <- ttl_map[common_stems]

count_nonempty_lines <- function(path) {
  sum(nzchar(trimws(readLines(path, warn = FALSE))))
}

Text_rows   <- vapply(soc_matched, count_nonempty_lines, integer(1))
Turtle_rows <- vapply(ttl_matched, count_nonempty_lines, integer(1))

df <- data.frame(
  file_stem = common_stems,
  Text_rows = Text_rows,
  Turtle_rows = Turtle_rows,
  stringsAsFactors = FALSE
)

ggplot(df, aes(x = Text_rows, y = Turtle_rows)) +
  geom_point() +
  labs(
    x = "Text rows",
    y = "Turtle rows"
  ) +
  theme_minimal()

X <- df[, c("Text_rows", "Turtle_rows")]
X_scaled <- scale(X)

wss <- sapply(1:10, function(k) {
  kmeans(X_scaled, centers = k, nstart = 25)$tot.withinss
})

elbow_df <- data.frame(
  k = 1:10,
  wss = wss
)

ggplot(elbow_df, aes(x = k, y = wss)) +
  geom_line(color = "#4C72B0", linewidth = 1.5) +
  geom_vline(xintercept = 3, 
             linetype = "dashed", 
             color = "#C44E52", 
             linewidth = 1) +
  scale_x_continuous(breaks = 1:10) +
  theme_minimal() +
  labs(
    x = "Number of clusters (k)",
    y = "WCSS"
  )
ggsave("elbow_method.png", width = 8, height = 4)

set.seed(123)
km <- kmeans(X_scaled, centers = 3, nstart = 25)

df$cluster <- factor(km$cluster)

df$expansion_ratio <- df$Turtle_rows / df$Text_rows

cluster_medians <- aggregate(
  cbind(Text_rows, Turtle_rows, expansion_ratio) ~ cluster,
  data = df,
  FUN = median
)

ordered_clusters <- cluster_medians$cluster[
  order(cluster_medians$Turtle_rows)
]

df$cluster_ordered <- factor(
  df$cluster,
  levels = ordered_clusters
)

ggplot(df, aes(Text_rows, Turtle_rows, color = cluster)) +
  geom_point(size = 5, alpha = 0.8) +
  scale_color_manual(values = c("#4C72B0", "#55A868", "#C44E52")) +
  theme_minimal() +
  labs(
    x = "Text rows in the SOC file (log scale)",
    y = "Text rows in the Turtle file (log scale)",
    color = "Cluster"
  ) +
  scale_x_log10() +
  scale_y_log10()

ggplot(df, aes(Text_rows, expansion_ratio, color = cluster)) +
  geom_point(size = 5, alpha = 0.8) +
  scale_color_manual(values = c("#4C72B0", "#55A868", "#C44E52")) +
  theme_minimal() +
  labs(
    x = "Text rows in the SOC file",
    y = "Expansion ratio",
    color = "Cluster"
  )
