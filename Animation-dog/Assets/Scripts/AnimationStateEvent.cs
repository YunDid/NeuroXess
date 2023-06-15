using System.Collections;
using System.Collections.Generic;
using System;
using UnityEngine;

public class AnimationStateEvent : StateMachineBehaviour
{

    public event Action<string> StateEntered;
    public event Action<string> StateExited;

    // OnStateEnter is called when a transition starts and the state machine starts to evaluate this state
    override public void OnStateEnter(Animator animator, AnimatorStateInfo stateInfo, int layerIndex)
    {
        // 获取状态名称
        string stateName = stateInfo.fullPathHash.ToString();
        // 触发状态进入事件
        StateEntered?.Invoke(stateName);
    }

    // OnStateUpdate is called on each Update frame between OnStateEnter and OnStateExit callbacks
    override public void OnStateUpdate(Animator animator, AnimatorStateInfo stateInfo, int layerIndex)
    {
       
    }

    // OnStateExit is called when a transition ends and the state machine finishes evaluating this state
    override public void OnStateExit(Animator animator, AnimatorStateInfo stateInfo, int layerIndex)
    {
        // 获取状态名称
        string stateName = stateInfo.fullPathHash.ToString();
        // 触发状态退出事件
        StateExited?.Invoke(stateName);
    }

    // OnStateMove is called right after Animator.OnAnimatorMove()
    //override public void OnStateMove(Animator animator, AnimatorStateInfo stateInfo, int layerIndex)
    //{
    //    // Implement code that processes and affects root motion
    //}

    // OnStateIK is called right after Animator.OnAnimatorIK()
    //override public void OnStateIK(Animator animator, AnimatorStateInfo stateInfo, int layerIndex)
    //{
    //    // Implement code that sets up animation IK (inverse kinematics)
    //}
    // public event Action<int> VariableChangedEvent;
}
