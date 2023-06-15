using System.Collections;
using System.Collections.Generic;
using System;
using UnityEngine;

public class DogControl : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        // 获取动画组件的引用
        animator = GetComponent<Animator>();
        CurrentStateInfo = new AnimationStateData();

        // 获取 AnimationStateEvent 脚本组件数据并依次订阅事件.

        StateEvents = animator.GetBehaviours<AnimationStateEvent>();

        foreach (var stateEvent in StateEvents)
        {
            stateEvent.StateEntered += OnStateEntered;
            stateEvent.StateExited += OnStateExited;
        }
    }

    private void OnDisable()
    {
        // 获取 AnimationStateEvent 脚本组件数据并依次取消订阅事件.
        foreach (var stateEvent in StateEvents)
        {
            stateEvent.StateEntered -= OnStateEntered;
            stateEvent.StateExited -= OnStateExited;
        }
    }


    // Update is called once per frame
    void Update()
    {

        // // 先判断是否有动画在播放
        // string name = IsAnyAnimationPlaying();
        // CurrentStateInfo.AnimationName = name;
        // Debug.Log(name);
        // if (CurrentStateInfo.AnimationName != "")
        // {
        //     isPlaying = true;
        //     CurrentStateInfo.IsPlaying = true;
        // }
        // else
        // {
        //     isPlaying = false;
        //     CurrentStateInfo.IsPlaying = false;
        // }

        // if (isPlaying)
        // {
        //     Debug.Log("CurrentAnimationName: " + CurrentStateInfo.AnimationName);
        //     Debug.Log("CurrentAnimationSpeed: " + CurrentStateInfo.Speed);
        //     // 检查动画播放状态
        //     if (IsAnimationFinished(CurrentStateInfo.AnimationName)) 
        //     {
        //         CurrentStateInfo.IsEndPlaying = true;
        //         Debug.Log(CurrentStateInfo.AnimationName + ": End.");
        //         isPlaying = false;
        //         CurrentStateInfo.IsPlaying = false;
        //         CurrentStateInfo.AnimationName = "";
        //     }
        //     // Debug.Log("CurrentAnimationName: " + CurrentStateInfo.AnimationName);
        //     // Debug.Log("CurrentAnimationName: " + CurrentStateInfo.AnimationName);
        // }
        // else 
        // {
        //     Debug.Log("No Animation is Playing.");
        // }

        // 检测输入并触发相应的动画状态转换
        if (Input.GetKeyDown(KeyCode.R))
        {
            PlayAnimation("LeftLeg");
        }
        else if (Input.GetKeyDown(KeyCode.F))
        {
            PlayAnimation("RightLeg");
        }
        else if (Input.GetKeyDown(KeyCode.V))
        {
            PlayAnimation("Idle");
        }

    }

    private void OnStateEntered(string stateName)
    {
        // 更新 CurrentStateInfo 字段属性，根据状态名称执行相应操作
        // ...
        Debug.Log(stateName + " : 开始播放");
    }

    private void OnStateExited(string stateName)
    {
        // 更新 CurrentStateInfo 字段属性，根据状态名称执行相应操作
        // ...
        Debug.Log(stateName + " : 播放完毕");

    }


    private void PlayAnimation(string animationName)
    {
        SetAnimationSpeed(speed);
        // 设置动画动态缓存
        CurrentStateInfo.AnimationName = animationName;
        CurrentStateInfo.Speed = speed;
        // 根据输入播放相应的动画状态
        animator.Play(CurrentStateInfo.AnimationName,0,0);
        isPlaying = true;
        CurrentStateInfo.IsPlaying = isPlaying;
    }

    private void SetAnimationSpeed(float speed)
    {
        animator.speed = speed;
    }

    // 检测动画状态是否播放完毕
    bool IsAnimationFinished(string stateName)
    {
        // 参数为动画层的索引.
        /*
            AnimatorStateInfo ：
            包含当前播放状态的信息.
            normalizedTime：动画的归一化时间，即当前动画播放的进度，范围为 0 到 1
            length：动画的总长度，以秒为单位
            speed：动画的播放速度
            tagHash：动画状态的标签的哈希值，用于标识不同的动画状态
            shortNameHash：动画状态的短名的哈希值，用于标识不同的动画状态
            
        */
        AnimatorStateInfo stateInfo = animator.GetCurrentAnimatorStateInfo(0);
        if (stateInfo.IsName(stateName))
        {
            
            Debug.Log("NormalizedTime" + stateInfo.normalizedTime);
            // 如果当前状态是指定的状态，并且播放时间超过动画的长度，则表示动画播放完毕
            if (stateInfo.normalizedTime >= 0.9f)
            {
                return true;
            }
        }
        return false;
    }

    public class AnimationStateData
    {
        // 动画切片名称
        public string AnimationName { get; set; }
        // 动画切片的播放速度
        public float Speed { get; set; }
        // 服务端 : 返回当前动画切片的播放状态
        public bool IsCorrect { get; set; }
        // 服务端 : 当前是否在播放动画
        public bool IsPlaying { get; set; }
        // 检测动画是否播放完毕
        public bool IsEndPlaying { get; set; }
        // 检测动画是否被打断
        public bool IsInterrupted { get; set; }
    }

    private Animator animator;
    public float speed = 1;

    private AnimationStateData CurrentStateInfo;
    private AnimationStateData PreStateInfo;
    private bool isPlaying = false;
    AnimationStateEvent[] StateEvents;
}