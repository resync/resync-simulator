#!/usr/bin/env Rscript  

# This scripts plots resync experiment results

# Dependencies:
# - ggplot2 (install.packages("ggplot2"))

# Run it as follows:
#   ./plot_figures.r data/results.csv

library(ggplot2)

# SETTING UP STUFF

# reading input files from command line args
args = commandArgs(TRUE)
results_file = args[1]

# the the output dir from the results file
output_path = file.path(dirname(normalizePath(results_file)), "plots")
dir.create(output_path, showWarnings = FALSE)

cat("Reading results file: ", results_file, "\n")
results = read.csv(file = results_file, head = TRUE, sep = ";")
cat("Read", nrow(results), "lines.\n")

# deriving and modifying columns
results$frac_changes = results$no_events / results$no_resources
results$no_resources = as.factor(results$no_resources)

print(results[, c("no_resources", "change_delay", "interval", "no_events", "frac_changes", "consistency")])

cat("*** START PLOTTING ***\n")

cat("Plotting Average Consistency\n")

p1 = ggplot(results, aes(x=change_delay, y=consistency, colour=no_resources) ) +
     geom_line() +
     facet_grid(interval ~ mode, labeller = label_both) +
     xlab("Change Interval (sec)") +
     ylab("Avg. Consistency")

filename = file.path(output_path, "average_consistency.png")
ggsave(p1, file = filename)

p2 = ggplot(results, aes(x=change_delay, y=latency, colour=no_resources) ) +
     geom_line() +
     facet_grid(interval ~ mode, labeller = label_both) +
     xlab("Change Interval (sec)") +
     ylab("Avg. Latency (sec)")

filename = file.path(output_path, "average_latency.png")
ggsave(p2, file = filename)

p3 = ggplot(results, aes(x=change_delay, y=efficiency, colour=no_resources) ) +
     geom_line() +
     facet_grid(interval ~ mode, labeller = label_both) +
     xlab("Change Interval (sec)") +
     ylab("Data Transfer Efficiency")

filename = file.path(output_path, "dt_efficiency.png")
ggsave(p3, file = filename)