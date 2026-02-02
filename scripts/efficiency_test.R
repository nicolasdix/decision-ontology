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

plot(1:10, wss, type = "b",
     xlab = "Number of clusters (k)",
     ylab = "Within-cluster sum of squares")

set.seed(42)
km <- kmeans(X_scaled, centers = 3, nstart = 25)

df$cluster <- factor(km$cluster)

ggplot(df, aes(Text_rows, Turtle_rows, color = cluster)) +
  geom_point(size = 4, alpha = 0.8) +
  scale_color_manual(values = c(
    "#6B705C",
    "#A5A58D",
    "#B5838D"
  )) +
  theme_minimal() +
  labs(
    color = "Cluster",
    x = "Number of text rows in the SOC file",
    y = "Number of text rows in the Turtle file"
  )

aggregate(cbind(Text_rows, Turtle_rows) ~ cluster,
          data = df,
          FUN = median)