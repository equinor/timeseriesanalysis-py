[CmdletBinding()]
param(
    [string]$AssemblyPath = (Join-Path $PSScriptRoot "..\_assemblies"),
    [switch]$NoPersistEnvironment
)

$ErrorActionPreference = "Stop"

$resolvedAssemblyPath = [IO.Path]::GetFullPath($AssemblyPath)
$temporaryRoot = Join-Path ([IO.Path]::GetTempPath()) ("timeseriesanalysis-" + [Guid]::NewGuid())
$packageIds = @("TimeSeriesAnalysis", "Accord", "Accord.Math", "Accord.Statistics", "Newtonsoft.Json")
$requiredAssemblies = @(
    "TimeSeriesAnalysis.dll",
    "Accord.dll",
    "Accord.Math.dll",
    "Accord.Math.Core.dll",
    "Accord.Statistics.dll",
    "Newtonsoft.Json.dll"
)

try {
    New-Item -ItemType Directory -Path $temporaryRoot -Force | Out-Null
    $assemblyFiles = @{}
    foreach ($packageId in $packageIds) {
        $packageIndexUri = "https://api.nuget.org/v3-flatcontainer/$($packageId.ToLowerInvariant())/index.json"
        $packageIndex = Invoke-RestMethod -Uri $packageIndexUri
        $version = @($packageIndex.versions) |
            Where-Object { $_ -notmatch "[-+]" } |
            Sort-Object { [Version]($_ -replace "-.*$", "") } -Descending |
            Select-Object -First 1

        if (-not $version) {
            throw "NuGet did not return a stable $packageId version."
        }

        $packagePath = Join-Path $temporaryRoot "$($packageId.ToLowerInvariant()).zip"
        $extractPath = Join-Path $temporaryRoot $packageId
        $packageUri = "https://api.nuget.org/v3-flatcontainer/$($packageId.ToLowerInvariant())/$($version.ToLowerInvariant())/$($packageId.ToLowerInvariant()).$($version.ToLowerInvariant()).nupkg"
        Write-Host "Downloading $packageId $version..."
        Invoke-WebRequest -Uri $packageUri -OutFile $packagePath
        Expand-Archive -Path $packagePath -DestinationPath $extractPath -Force

        foreach ($assembly in $requiredAssemblies | Where-Object { -not $assemblyFiles.ContainsKey($_) }) {
            $match = Get-ChildItem -Path $extractPath -Filter $assembly -File -Recurse |
                Where-Object { $_.FullName -match "[\\/]lib[\\/]" } |
                Select-Object -First 1

            if ($match) {
                $assemblyFiles[$assembly] = $match.FullName
            }
        }
    }

    foreach ($assembly in $requiredAssemblies) {
        if (-not $assemblyFiles.ContainsKey($assembly)) {
            throw "Could not find $assembly in the downloaded NuGet packages."
        }
    }

    New-Item -ItemType Directory -Path $resolvedAssemblyPath -Force | Out-Null
    foreach ($assembly in $requiredAssemblies) {
        Copy-Item -Path $assemblyFiles[$assembly] -Destination (Join-Path $resolvedAssemblyPath $assembly) -Force
    }

    $env:TIMESERIESANALYSIS_ASSEMBLY_PATH = $resolvedAssemblyPath
    if (-not $NoPersistEnvironment) {
        [Environment]::SetEnvironmentVariable(
            "TIMESERIESANALYSIS_ASSEMBLY_PATH",
            $resolvedAssemblyPath,
            [EnvironmentVariableTarget]::User
        )
    }

    Write-Host "Installed required assemblies to $resolvedAssemblyPath"
    if ($NoPersistEnvironment) {
        Write-Host "Set TIMESERIESANALYSIS_ASSEMBLY_PATH for this PowerShell session only."
    } else {
        Write-Host "Set TIMESERIESANALYSIS_ASSEMBLY_PATH for this session and future user sessions."
    }
}
finally {
    if (Test-Path $temporaryRoot) {
        Remove-Item -Path $temporaryRoot -Recurse -Force
    }
}