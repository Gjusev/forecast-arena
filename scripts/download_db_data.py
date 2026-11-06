"""Download the monthly processed DB delay parquets (finalized per-stop records).

~1.7 GB across 28 files; cached by huggingface_hub. Run once.
"""

from huggingface_hub import snapshot_download

REPO = "piebro/deutsche-bahn-data"

path = snapshot_download(
    repo_id=REPO,
    repo_type="dataset",
    allow_patterns=["monthly_processed_data/*.parquet"],
    max_workers=4,
)
print("downloaded to:", path)
