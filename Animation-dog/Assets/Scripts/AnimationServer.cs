using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;

public class AnimationServer : MonoBehaviour
{
    private TcpListener tcpListener;
    private TcpClient connectedClient;

    public Animator animator;
    public int port = 8888;

    // 使用队列存储客户端事件消息
    // private Queue<string> animationQueue = new Queue<string>();

    // 保护共享资源的互斥锁
    //private object queueLock = new object();

    // ConcurrentQueue Unity 内部已经实现了线程安全，无需自行加锁
    private ConcurrentQueue<string> animationQueue = new ConcurrentQueue<string>();

    private void Start()
    {
        // 获取动画组件的引用
        animator = GetComponent<Animator>();

        // 启动服务器
        tcpListener = new TcpListener(IPAddress.Any, port);
        tcpListener.Start();
        Debug.Log("Server started. Waiting for client...");

        // 在后台线程监听客户端连接
        System.Threading.Tasks.Task.Run(() => ListenForClient());
    }

    private void Update()
    {
        // 在主线程中处理接收到的动画事件并执行动画播放操作
        ProcessReceivedAnimations();
    }

    private void ListenForClient()
    {
        connectedClient = tcpListener.AcceptTcpClient();
        Debug.Log("Client connected.");

        // 在后台线程监听客户端消息
        System.Threading.Tasks.Task.Run(() => ReceiveMessages());
    }

    private void ReceiveMessages()
    {
        byte[] buffer = new byte[1024];
        NetworkStream stream = connectedClient.GetStream();

        while (true)
        {
            try
            {
                // 清空缓冲区
                // Array.Clear(buffer, 0, buffer.Length);
                
                // 读取客户端发送的数据
                int bytesRead = stream.Read(buffer, 0, buffer.Length);
                string message = Encoding.ASCII.GetString(buffer, 0, bytesRead);

                Debug.Log("Test log animationName: " + message);

                // // 根据接收到的消息触发相应的模型动画
                // switch (message)
                // {
                //     case "Attack":
                //         PlayAnimation("Attack");
                //         break;
                //     case "Pissing":
                //         PlayAnimation("Pissing");
                //         break;
                //     case "Death":
                //         PlayAnimation("Death");
                //         break;
                //     // 添加其他需要处理的消息和相应的动画触发逻辑
                //     default:
                //         Debug.Log("Unknown message: " + message);
                //         break;
                // }

                // 将接收到的动画事件添加到队列中
                if(message != "")
                    animationQueue.Enqueue(message);
            }
            catch (Exception e)
            {
                Debug.Log("Error receiving message: " + e.Message);
                break;
            }
        }

        stream.Close();
        connectedClient.Close();
        Debug.Log("Client disconnected.");
    }

    private void PlayAnimation(string animationName)
    {
        // 在主线程中触发模型动画
        UnityMainThreadDispatcher.Instance.Enqueue(() =>
        {
            animator.Play(animationName);
        });
        // Debug.Log("Error receiving message: " + animationName);
    }

    private void ProcessReceivedAnimations()
    {
        // lock (queueLock)
        // {
        //     while (animationQueue.Count > 0)
        //     {
        //         string animationName = animationQueue.Dequeue();
        //         Debug.Log("animationName: " + animationName);
        //         PlayAnimation(animationName);
        //     }
        // }

        // 在主线程中处理动画事件队列
        while (animationQueue.TryDequeue(out string animationName))
        {
            // 处理动画事件
            Debug.Log("animationName: " + animationName);
            PlayAnimation(animationName);
        }
    }
}
