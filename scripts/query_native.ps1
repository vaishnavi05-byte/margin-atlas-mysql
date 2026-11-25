param([Parameter(Mandatory=$true)][int]$Port,
      [Parameter(Mandatory=$true)][string]$LibraryFolder,
      [string]$QueryFile = "$PSScriptRoot/../tests/native_checks.dax",
      [string]$OutputFile = "$PSScriptRoot/../docs/native-dax-results.json")
$ErrorActionPreference='Stop'
foreach ($dllName in @('Microsoft.AnalysisServices.Runtime.Core.dll','Microsoft.AnalysisServices.Runtime.Windows.dll','Microsoft.AnalysisServices.AdomdClient.dll')) {
  [System.Reflection.Assembly]::LoadFrom((Join-Path $LibraryFolder $dllName)) | Out-Null
}
$connection = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection "Data Source=localhost:$Port"
try {
  $connection.Open()
  $command=$connection.CreateCommand()
  $command.CommandText=Get-Content -LiteralPath $QueryFile -Raw
  $reader=$command.ExecuteReader()
  $results=@()
  do {
    $rows=@()
    while ($reader.Read()) {
      $row=[ordered]@{}
      for ($i=0;$i -lt $reader.FieldCount;$i++) { $row[$reader.GetName($i)]=if($reader.IsDBNull($i)){$null}else{$reader.GetValue($i)} }
      $rows+=,$row
    }
    $results+=,[ordered]@{rows=$rows}
  } while ($reader.NextResult())
  New-Item -ItemType Directory -Path (Split-Path $OutputFile) -Force | Out-Null
  $results | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputFile -Encoding utf8
  Write-Output "Saved $($results.Count) read-only DAX result sets."
} finally { $connection.Close() }
