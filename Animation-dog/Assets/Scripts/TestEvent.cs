// using UnityEngine;
// using System;
// using System.Net.Sockets;
// using System.Text;
// using System.Threading;

// public class TestEvent : MonoBehaviour
// {
//     // 定义事件用于线程间通信
//     private AutoResetEvent eventSignal = new AutoResetEvent(false);
//     private string currentAnimation;

//     // 在主线程中更新动画状态
//     private void Update()
//     {
//         // 处理实时接收到的客户端消息
//         // 参数若设置为0，则不会阻塞当前线程，否则会阻塞等待.
//         if (eventSignal.WaitOne(0))
//         {
//             PlayAnimation(currentAnimation);
//         }
//     }

//     // 监听客户端连接并处理消息
//     private void ListenForClient()
//     {
//         while (true)
//         {
//             // 接收到客户端消息后触发事件
//             string message = ReceiveMessage();
//             currentAnimation = message;
//             eventSignal.Set();
//         }
//     }

//     // 模拟接收客户端消息
//     private string ReceiveMessage()
//     {
//         // 假设在这里接收到客户端的消息
//         // 返回相应的动画名称
//         return "Attack";
//     }

//     // 播放动画
//     private void PlayAnimation(string animationName)
//     {
//         // 在主线程中触发模型动画
//         UnityMainThreadDispatcher.Instance.Enqueue(() =>
//         {
//             animator.Play(animationName);
//         });
//     }
// }
