param(
    [Parameter()]
    [String]$type = "release"
)


$PYTHON_PATH = Split-Path (Get-Command python).Path

#$RESOURCES = "$PWD\assets;assets"
$EMOUSE = "$PWD\eMouse;eMouse"
$version="0.0.1"
$name="me-decoder-${type}"
$Env:RM_CONSOLE_LOG="yes"
$RESOURCES="$PWD/venv/Lib/site-packages/spectrum-0.8.1-py3.10-win-amd64.egg/;spectrum-0.8.1-py3.10-win-amd64.egg/"
$spectrum="$PWD/venv/Lib/site-packages/spectrum-0.8.1-py3.10-win-amd64.egg/spectrum;spectrum/"
$sklearn="$PWD/venv/Lib/site-packages/sklearn;sklearn"

if ( $type -eq 'debug' ){
    Write-Output "PyInstaller -n ${name}  -F -w app/decoder_main.py"
    python -m PyInstaller -n "${name}" --add-data $RESOURCES --add-data $spectrum --add-data $sklearn --hiddenimport=sklearn --collect-submodules numpy.distutils --hiddenimport distutils.unixccompiler  --hiddenimport=numpy.distutils  -F  app/decoder_main.py
}else{
    Write-Output "PyInstaller -n ${name} --add-data $RESOURCES -F -w app/decoder_main.py"
    python -m PyInstaller -n "${name}" --add-data $RESOURCES --hiddenimport=numpy.distutils --hiddenimport=sklearn -F -w app/decoder_main.py
}


# python -m PyInstaller ./NxGame.spec

