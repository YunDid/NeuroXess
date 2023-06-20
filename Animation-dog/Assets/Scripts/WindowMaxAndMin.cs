using UnityEngine;
using System.Collections;

public class WindowMaxAndMin : MonoBehaviour
{
    //切换
    private bool switchover;

    private void Awake()
    {
        switchover = false;       
        Screen.SetResolution(1920, 1080, switchover);        
    }

    // Update is called once per frame
    void Update()
    {
        //  按Control切换全屏或者窗口模式      
        if (Input.GetKey(KeyCode.LeftControl) || Input.GetKey(KeyCode.RightControl))
        {
            switchover = !switchover;
            Screen.SetResolution(1920, 1080, switchover);
            Screen.fullScreen = switchover;  
        }

    }
}