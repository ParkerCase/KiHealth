# R script: read the .sav and .por files that pyreadstat could not read,
# and export them to CSV so you can view them.
#
# Requires: R with package 'haven' (install.packages("haven"))
#
# Usage (from project root):
#   export DATA_ROOT="$(pwd)/data/New-OA-Data"
#   Rscript scripts/run_r_export_unreadable.R
#
# Or from R:
#   Sys.setenv(DATA_ROOT = "path/to/DOC/data/New-OA-Data")
#   source("scripts/run_r_export_unreadable.R")

base_dir <- Sys.getenv("DATA_ROOT")
if (is.null(base_dir) || base_dir == "") {
  stop("Set DATA_ROOT to the path to data/New-OA-Data, e.g. export DATA_ROOT=\"$(pwd)/data/New-OA-Data\"")
}

if (!requireNamespace("haven", quietly = TRUE)) {
  stop("Install the 'haven' package: install.packages(\"haven\")")
}

# Unreadable .sav files (stem names only)
list_of_sav <- c(
  "Lt01_e", "Lt02_e", "Lt03_e", "Lt04_e", "Lt05_e", "Lt06_e", "Lt07_e", "Lt08_e",
  "str01_e", "str02_e", "str03_e", "str04_e", "str05_e", "str06_e", "str07_e", "str08_e",
  "w01_e", "w02_e", "w03_e", "w04_e", "w05_e", "w05_new_e", "w06_e", "w07_e", "w08_e"
)

out_sav <- file.path(base_dir, "extracted", "sav_from_r")
out_por <- file.path(base_dir, "extracted", "por_from_r")
dir.create(out_sav, recursive = TRUE, showWarnings = FALSE)
dir.create(out_por, recursive = TRUE, showWarnings = FALSE)
spss_dir <- file.path(base_dir, "KLoSa", "KLoSA 1-9th wave (SPSS)")

for (stem in list_of_sav) {
  f <- file.path(spss_dir, paste0(stem, ".sav"))
  if (!file.exists(f)) {
    message("Skip (not found): ", stem)
    next
  }
  out_csv <- file.path(out_sav, paste0(stem, ".csv"))
  out_vars <- file.path(out_sav, paste0(stem, "_variables.txt"))
  tryCatch({
    d <- haven::read_sav(f)
    write.csv(d, out_csv, row.names = FALSE)
    writeLines(names(d), out_vars)
    message("OK: ", stem, " (", nrow(d), " rows, ", ncol(d), " cols)")
  }, error = function(e) {
    message("FAIL ", stem, ": ", conditionMessage(e))
  })
}

# CHECK radiographic .por
por_file <- file.path(base_dir, "CHECK", "CHECK_Radiographic_Scoring_OA_T0T2T5T8T10_DANS_nsinENG_20170726.por")
if (file.exists(por_file)) {
  tryCatch({
    d <- haven::read_por(por_file)
    out_csv <- file.path(out_por, "CHECK_Radiographic_OA_T0T2T5T8T10.csv")
    write.csv(d, out_csv, row.names = FALSE)
    writeLines(names(d), file.path(out_por, "CHECK_Radiographic_variables.txt"))
    message("OK: CHECK radiographic .por (", nrow(d), " rows, ", ncol(d), " cols)")
  }, error = function(e) {
    message("FAIL .por: ", conditionMessage(e))
  })
} else {
  message("CHECK .por file not found: ", por_file)
}

message("Done. Check: ", out_sav, " and ", out_por)
