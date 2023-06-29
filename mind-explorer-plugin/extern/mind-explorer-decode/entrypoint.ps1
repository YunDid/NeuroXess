# 获取workdir
function Get-RootPath{
    $root_file = 'requirements.txt'
    $rootpath = Get-Location
    ForEach ($number in 1..5 ) {
        if ( Test-Path $root_file ){
            $rootpath = Get-Location
            #Write-Output "Current workdir is $rootpath\n"
            break
        }else{
            cd ..
        }
    }
    return $rootpath
}

$rootpath = Get-RootPath
# Write-Output Get-RootPath

# 设置python_path
$Env:PYTHONPATH = $rootpath

# 日志级别
# if ( !$Env:LOGURU_LEVEL ) {
#     $Env:LOGURU_LEVEL = "INFO"
# }

# 读取环境变量文件路径
if ( !$Env:ENV_PATH ) {
    $Env:ENV_PATH = '.env'
}


# 加载venv
if ( Test-Path venv ) {
    Write-Output "load venv"
    venv/Scripts/activate.ps1
}

# 安装依赖
pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

$Env:Path = $Env:Path + ";C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.35.32215\bin\Hostx64\x64"
Write-Output "PYTHONPATH=$Env:PYTHONPATH; LOGURU_LEVEL=$Env:LOGURU_LEVEL; envpath=$Env:ENV_PATH; $Env:Path"

Write-Output "ARGS=$args"

python  app/main.py $args

