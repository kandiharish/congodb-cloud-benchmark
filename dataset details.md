The Kaggle dataset I downloaded is currently available in a folder named:

`archive`

Treat `archive` as the original downloaded dataset/acquisition folder.

Do not delete or modify the original files inside `archive`.

First inspect its contents and identify:

* relationship/edge file
* profile/user data file, if present
* file formats
* approximate record counts
* headers/comments
* delimiter
* compression status

Then organize the project as:

```text
data/
├── downloads/
│   └── archive/
│
├── raw/
│   └── [original extracted dataset files]
│
├── processed/
│
├── metadata.json
└── README.md
```

Move/copy the `archive` folder into `data/downloads/` only if necessary. Prefer copying rather than destroying the original source.

Do NOT:

* modify the original dataset
* sample the dataset
* filter relationships
* change IDs
* change relationship direction
* create the final benchmark subset
* connect to databases
* run benchmarks

For this milestone, ONLY inspect, organize, and validate the downloaded dataset.

After inspection, report exactly:

1. Files found inside `archive`
2. Which file contains relationships
3. Which file contains profiles, if any
4. File sizes
5. Number of records if safely measurable
6. Data format
7. Any issues
8. Recommended next step

STOP after this inspection.
