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
if (is.na(results_file)) results_file = c("./data/results.csv")

cat("Reading results file: ", results_file, "\n")
results = read.csv(file = results_file, head = TRUE, sep = ";")
cat("Read", nrow(results), "lines.\n")

cat("*** START PLOTTING ***\n")

cat("Plotting resource consistency\n")

p1 = ggplot(results, aes(as.numeric(no_resources))) +
     geom_line( aes(y = consistency) ) +
     facet_grid(change_delay ~ interval, labeller = label_both) +
     labs(title = "Average Resource Consistency") +
     xlab("Number of Resources") +
     ylab("Avg. Consistency") +
     scale_x_log10()

# plot(p1)
ggsave(p1, file = "resync_consistency_1.png")

p2 = ggplot(results, aes(x=change_delay, y=consistency, colour=as.factor(no_resources))) +
     geom_line() +
     facet_grid(interval ~ ., labeller = label_both) +
     labs(title = "Average Resource Consistency") +
     xlab("Change Delay (sec)") +
     ylab("Avg. Consistency") +
     scale_x_log10()

ggsave(p2, file = "resync_consistency_2.png")
