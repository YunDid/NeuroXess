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

$job1 = Start-Job -ScriptBlock { python D:\develop\py\mind-explorer-plugin\tools\simulator\pub_eeg.py }
$job2 = Start-Job -ScriptBlock { python D:\develop\py\mind-explorer-plugin\tools\simulator\imu.py }
Wait-Job $job2
#Receive-Job -Job $job
#
#python D:\develop\py\mind-explorer-plugin\tools\simulator\pub_eeg.py
#python D:\develop\py\mind-explorer-plugin\tools\simulator\imu.py