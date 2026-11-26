# Run the native Spark demo from the project-local Python environment.
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $python = (Resolve-Path '.venv/Scripts/python.exe').Path
    $env:PYSPARK_PYTHON = $python
    $env:PYSPARK_DRIVER_PYTHON = $python
    $env:SPARK_LOCAL_IP = '127.0.0.1'
    $out = 'extras/spark-run'
    New-Item -ItemType Directory -Force $out | Out-Null

    & $python -u -c "import pyspark, sys; print('Python', sys.version.split()[0], '/ PySpark', pyspark.__version__); from src.etl.etl_pipeline import run_etl; run_etl(output_dir='evaluation/spark-run')" |
        Tee-Object "$out/etl.log"
    if ($LASTEXITCODE -ne 0 -or !(Select-String -Quiet -SimpleMatch 'Successfully completed Spark ETL' "$out/etl.log")) {
        throw 'The native Spark ETL did not complete. See the terminal and etl.log.'
    }
    & $python -u src/models/train_pyspark_mllib.py | Tee-Object "$out/mllib.log"
    if ($LASTEXITCODE -ne 0 -or !(Select-String -Quiet -SimpleMatch 'Complete suite execution successful!' "$out/mllib.log")) {
        throw 'The MLlib run did not finish. See the terminal and mllib.log.'
    }
} finally {
    Pop-Location
}
