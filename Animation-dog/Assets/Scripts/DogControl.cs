using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DogControl : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        // 获取动画组件的引用
        animator = GetComponent<Animator>();
    }

    // Update is called once per frame
    void Update()
    {
         // 检测输入并触发相应的动画状态转换
        if (Input.GetKeyDown(KeyCode.Q))
        {
            PlayAnimation(1);
        }
        else if (Input.GetKeyDown(KeyCode.E))
        {
            PlayAnimation(2);
        }
        else if (Input.GetKeyDown(KeyCode.W))
        {
            PlayAnimation(3);
        }
    }

    private void PlayAnimation(int animationIndex)
    {
        
        SetAnimationSpeed(speed);
        // 根据输入的数字播放相应的动画状态
        switch (animationIndex)
        {
            case 1:
                animator.Play("LeftLeg");
                break;
            case 2:
                animator.Play("RightLeg");
                break;
            case 3:
                animator.Play("Death");
                break;
            default:
                Debug.LogError("Invalid animation index");
                break;
        }
    }

    private void SetAnimationSpeed(float speed)
    {
        animator.speed = speed;
    }

    private Animator animator;
    public float speed = 1;
}