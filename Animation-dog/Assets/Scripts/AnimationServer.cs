using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;
using Newtonsoft.Json;

public class AnimationServer : MonoBehaviour
{
    private TcpListener tcpListener;
    private TcpClient connectedClient;

    public Animator animator;
    public int port = 8888;
    //Test Speed
    public float anispeed;

    // 使用队列存储客户端事件消息
    // private Queue<string> animationQueue = new Queue<string>();

    // 保护共享资源的互斥锁
    //private object queueLock = new object();

    // ConcurrentQueue Unity 内部已经实现了线程安全，无需自行加锁
    private ConcurrentQueue<AnimationData> animationQueue = new ConcurrentQueue<AnimationData>();

    public class AnimationData
    {   
        // 动画切片名称
        public string AnimationName { get; set; }
        // 动画切片的播放速度
        public float Speed { get; set; }
        // 客户端 : 设置是否需要返回当前动画切片的播放状态
        public bool NeedReturnStateFlag { get; set; }
    }

    public class AnimationStateData
    {
        // 动画切片名称
        public string AnimationName { get; set; }
        // 动画切片的播放速度
        public float Speed { get; set; }
        // 服务端 : 返回当前动画切片的播放状态
        public bool IsCorrect { get; set; }
    }

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

        // 读取或写入字节数据的对象.
        NetworkStream stream = connectedClient.GetStream();

        try
        {
            while (connectedClient.Connected)
            {
                // 返回读取字节流中的实际字节数.
                // 阻塞方法，若没有字节可读，将阻塞当前线程.
                int bytesRead = stream.Read(buffer, 0, buffer.Length);
                // 这个 bytesRead 的指针是否会移动，否则暂存缓存会导致判断不准确.
                if (bytesRead > 0)
                {
                    // string message = Encoding.ASCII.GetString(buffer, 0, bytesRead);

                    // Debug.Log("Test log animationName: " + message);

                    // // 将接收到的动画事件添加到队列中
                    // animationQueue.Enqueue(message);

                    // 添加其他根据接收字段需要处理的事件.
                    string jsonString = Encoding.ASCII.GetString(buffer, 0, bytesRead);

                    // 反序列化 JSON 字符串为自定义数据结构
                    AnimationData receivedData = JsonConvert.DeserializeObject<AnimationData>(jsonString);

                    // 可以访问 receivedData 的各个字段并进行相应处理
                    Debug.Log("AnimationName: " + receivedData.AnimationName);
                    Debug.Log("Speed: " + receivedData.Speed);

                    if (receivedData.NeedReturnStateFlag)
                    {
                       System.Threading.Tasks.Task.Run(() => SendMessages(ref stream));
                    }

                    // 没有加条件处理消息字段的可靠性.
                    // 将接收到的动画属性字段入队列.
                    animationQueue.Enqueue(receivedData);
                }
                else
                {
                    // 客户端断开连接
                    // 可以于此设置延时等待.
                    break;
                }
            }
        }
        catch (Exception e)
        {
            Debug.Log("Error receiving message: " + e.Message);
        }

        stream.Close();
        connectedClient.Close();
        Debug.Log("Client disconnected.");
    }

    private void SendMessages(ref NetworkStream stream) 
    {
        // 创建返回对象.
        AnimationStateData returnStateData = new AnimationStateData();
        returnStateData.AnimationName = "This is the return state message.";
        returnStateData.Speed = 10;
        returnStateData.IsCorrect = true;

        // Serialize the response object to JSON
        string response = JsonConvert.SerializeObject(returnStateData);

        // Send the response to the client
        byte[] responseBuffer = Encoding.ASCII.GetBytes(response);
        stream.Write(responseBuffer, 0, responseBuffer.Length);
    }

    private void PlayAnimation(AnimationData animation)
    {
        // 在主线程中触发模型动画
        UnityMainThreadDispatcher.Instance.Enqueue(() =>
        {
            animator.speed = animation.Speed;
            animator.Play(animation.AnimationName);
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
        while (animationQueue.TryDequeue(out AnimationData animation))
        {
            // 处理动画事件
            Debug.Log("animationName: " + animation.AnimationName);
            Debug.Log("animationSpeed: " + animation.Speed);
            // 目前接口写死，这个速度或者其余控制参数都可以通过字段传递，目前仅作测试用
            PlayAnimation(animation);
        }
    }

}

