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
    private bool isPlayingAnimation = false;

    // 使用队列存储客户端事件消息
    // private Queue<AnimationData> animationQueue = new Queue<AnimationData>();

    // 保护共享资源的互斥锁
    //private object queueLock = new object();

    // ConcurrentQueue Unity 内部已经实现了线程安全，无需自行加锁
    private ConcurrentQueue<AnimationData> animationQueue = new ConcurrentQueue<AnimationData>();
    // 获取 Behaviour 组件数组(包含动画状态事件)
    AnimationStateEvent[] StateEvents;
    // 当前播放动画的状态信息
    AnimationStateData CurrentStateInfo;
    // 协程标志位，确保只有一个协程执行
    bool isCoroutineRunning = false;
    // 是否有除Idle外的其他状态在播放
    private bool isPlaying = false;

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
        // 服务端 : 当前是否在播放动画
        public bool IsPlaying { get; set; }
        // 检测动画是否播放完毕
        public bool IsEndPlaying { get; set; }
        // 检测动画是否被打断
        public bool IsInterrupted { get; set; }

    }

    private void Start()
    {
        // 获取动画组件的引用
        animator = GetComponent<Animator>();

        // 获取 AnimationStateEvent 脚本组件数据并依次订阅事件.

        StateEvents = animator.GetBehaviours<AnimationStateEvent>();

        foreach (var stateEvent in StateEvents)
        {
            stateEvent.StateEntered += OnStateEntered;
            stateEvent.StateExited += OnStateExited;
        }

        // 创建动画状态信息缓存，内存释放甭管，先运行，内部应该有默认初始化操作
        CurrentStateInfo = new AnimationStateData();
        CurrentStateInfo.IsEndPlaying = true;

        // 启动服务器
        tcpListener = new TcpListener(IPAddress.Any, port);
        tcpListener.Start();
        Debug.Log("Server started. Waiting for client...");

        // 在后台线程监听客户端连接
        System.Threading.Tasks.Task.Run(() => ListenForClient());
        // test();

        // 启动协程监听队列
        // StartCoroutine(ProcessReceivedAnimations());
    }

    void test() 
    {
       int count = 0;
       while(true)
       {
            AnimationData TestAni = new AnimationData();
            if(count % 2==0)
                TestAni.AnimationName = "LeftLeg";
            else
                TestAni.AnimationName = "RightLeg";
            TestAni.Speed = 1.0f;
            animationQueue.Enqueue(TestAni);

            count++;
            if(count == 100) 
            {
                break;
            }
       }
    }

    private void Update()
    {
        // 在主线程中处理接收到的动画事件并执行动画播放操作
        // if(!CurrentStateInfo.IsPlaying)
        // ProcessReceivedAnimations();
        // 启动协程播放动画，防止被频繁打断导致动画仅播放一个
        if (!isCoroutineRunning && !animationQueue.IsEmpty)
        {
            StartCoroutine(ProcessReceivedAnimations());
        }

        // 逐帧输出当前状态信息
        Debug.Log("AnimationName : " + CurrentStateInfo.AnimationName);
        Debug.Log("Speed : " + CurrentStateInfo.Speed);
        Debug.Log("IsPlaying : " + CurrentStateInfo.IsPlaying);
        Debug.Log("IsCorrect + " + CurrentStateInfo.IsCorrect);
        Debug.Log("IsEndPlaying : " + CurrentStateInfo.IsEndPlaying);
        Debug.Log("IsInterrupted : " + CurrentStateInfo.IsInterrupted);
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

    private void OnStateEntered(string stateName)
    {
        
        isPlaying = true;
        // 更新 CurrentStateInfo 字段属性，根据状态名称执行相应操作

        CurrentStateInfo.AnimationName = stateName;
        CurrentStateInfo.Speed = animator.speed;
        CurrentStateInfo.IsPlaying = true;
        // 理论上被打断的时候设置为 fasle ，需要完善
        CurrentStateInfo.IsCorrect = true;
        CurrentStateInfo.IsEndPlaying = false;
        CurrentStateInfo.IsInterrupted = false;
        // Debug.Log(stateName + " : 开始播放");
    }

    private void OnStateExited(string stateName)
    {
        
        isPlaying = false;
        // 更新 CurrentStateInfo 字段属性，根据状态名称执行相应操作
        CurrentStateInfo.AnimationName = "";
        CurrentStateInfo.Speed = animator.speed;
        CurrentStateInfo.IsPlaying = false;
        // 理论上被打断的时候设置为 fasle ，需要完善
        CurrentStateInfo.IsCorrect = true;
        CurrentStateInfo.IsEndPlaying = true;
        CurrentStateInfo.IsInterrupted = false;
        // Debug.Log(stateName + " : 播放完毕");
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
                    Debug.Log("ReceiveMessages AnimationName: " + receivedData.AnimationName);
                    Debug.Log("ReceiveMessages Speed: " + receivedData.Speed);

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

        // 重新监听
        System.Threading.Tasks.Task.Run(() => ListenForClient());
    }

    private void SendMessages(ref NetworkStream stream) 
    {
        // 创建返回对象.
        // AnimationStateData returnStateData = new AnimationStateData();
        // returnStateData.AnimationName = "This is the return state message.";
        // returnStateData.Speed = 10;
        // returnStateData.IsCorrect = true;

        // Serialize the response object to JSON
        string response = JsonConvert.SerializeObject(CurrentStateInfo);

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
           animator.Play(animation.AnimationName, 0, 0);
           isPlayingAnimation = true;

        //    Debug.Log("PlayAnimation speed: " + animation.Speed);
        });
        // Debug.Log("Error receiving message: " + animationName);
        // Debug.Log("PlayAnimation animationName: " + animation.AnimationName);

    }

    private IEnumerator ProcessReceivedAnimations()
    {
        isCoroutineRunning = true;

        // 在主线程中处理动画事件队列
        while (animationQueue.TryDequeue(out AnimationData animation))
        {
            Debug.Log("ProcessReceivedAnimations QueueLength : " + animationQueue.Count);
            // 处理动画事件
            // Debug.Log("ProcessReceivedAnimations animationName: " + animation.AnimationName);
            // Debug.Log("ProcessReceivedAnimations animationSpeed: " + animation.Speed);
            // 通过字段属性控制切片的播放
            PlayAnimation(animation);
            // 等待动画播放完毕
            // yield return new WaitUntil(() => IsAnimationFinished());
            // 等待一段时间
            float time = 0.45f / (animation.Speed);
            yield return new WaitForSeconds(time);
        }

        isCoroutineRunning = false;
    }

    // 检测动画状态是否播放完毕 尚不完善.
    bool IsAnimationFinished()
    {
        return !isPlaying;
    }

}

