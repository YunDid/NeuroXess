param(
    [Parameter()]
    [String]$type = "release"
)


$PYTHON_PATH = Split-Path (Get-Command python).Path

#$RESOURCES = "$PWD\assets;assets"
$EMOUSE = "$PWD\eMouse;eMouse"
$version="0.0.2"
$name="me-plugin-${type}"
$Env:RM_CONSOLE_LOG="yes"
$RESOURCES="$PWD/venv/Lib/site-packages/spectrum-0.8.1-py3.10-win-amd64.egg/;spectrum-0.8.1-py3.10-win-amd64.egg/"
$spectrum="$PWD/venv/Lib/site-packages/spectrum-0.8.1-py3.10-win-amd64.egg/spectrum;spectrum/"

if ( $type -eq 'debug' ){
    Write-Output "PyInstaller -n ${name}  -F -w .\main.py"
    python -m PyInstaller -n "${name}" --add-data $RESOURCES --add-data $spectrum  --collect-submodules numpy.distutils --hiddenimport distutils.unixccompiler  --hiddenimport=numpy.distutils  -F -c .\main.py
}else{
    Write-Output "PyInstaller -n ${name} --add-data $RESOURCES -F -w .\main.py"
    python -m PyInstaller -n "${name}" --add-data $RESOURCES --hiddenimport=numpy.distutils -F -w .\main.py
}


# python -m PyInstaller ./NxGame.spec

