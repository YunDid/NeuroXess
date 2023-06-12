# NeuroXess

> 实习记录.

# 2023.6.7

- ~~入职相关准备.~~

  > wifi,电脑.

- 环境配置.

  > 相关开发软件安装.

- gitlab项目拉取.

  > SSH 密钥生成.

- 企业邮箱.

  > zhiyun.ma@neuroxess.com
  >
  > mzfyjyjy8888.

- 网络传输.

  > OKJH: 
  >
  > Administrator
  >
  > Passw0rd

- Qt.

  > 默认组件.
  >
  > 6.6.0.

- Vscode.

  > 拓展配置需要的环境.
  >
  > Cpp.
  >
  > Python.

- Github

  > Token : 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

# 2023.6.8

1. 基于Unity制作拉布拉多犬动画(资源购买)，通过操纵杆触发三种事件.

> 操作输入映射问题，先默认wasd键盘输入触发动画资源.
>

 - 迈左腿

 - 迈右腿

 - 保持静止


2. 项目打包.

 3. 操纵杆操纵数据通过网络在线传输.

    > 尝试 Server，创建配置文件启动加载.

 4. 性能优化.

    > 资源占用问题.

数据格式 事件

雷哥对接

# 2023.6.9

> 实现Unity可操纵三种状态响应的拉布拉多犬demo.

1. 模型获取.

   - 模型类型: 拉布拉多犬.

   - 模型状态: 除抬腿外，还有多种状态.

   - **模型动画切片类型存在问题，待解决.**

     > 对动画切片进行切割可能解决该问题.

2. 完成基本的 **Unity 事件**响应，触发动画.

   > 先通过键盘 Q,W,E 简单事件触发三种状态.
   >
   > 任何事件都可触发动画.

   - 通过 Animator 触发动画，并基于动画参数实现**状态转换.**

     > 问题在于这三种状态是否需要状态直接的切换，还是说仅仅想moba游戏一样直接触发技能那种就行.
     >
     > **状态只能触发一次，具化需求时需要看一下具体的接口下的动画切片调用逻辑**

   - 通过旧版 Animation 直接触发动画，而不是动画的切换.

     > 如果不需要过渡，只需要单独每个动画播放结束后复原即可.

**目前并不理解需求目标，需要完成这个阶段后再次对接.**

**v1.0需求明确：**

1. 作为 Server 接收客户端连接请求，客户端发送控制指令完成事件的触发. **- 完成**

   > 目前连接已经建立，但是数据解析有问题，Server 对于 Client 发来的数据无法正确解析.
   >
   > 当前 Client 的控制指令必须为 Qstring 字符串，指明要播放的动画状态名称。例如 RaiseLeft - 播放抬起左腿动画.

2. Unity 端只需要两种动画并提供可触发动画的接口即可. **- 完成**

   > 控制方式需要客户端调整，Timeing.

3. 项目打包. **- 完成**

   > 可针对指定平台进行打包，exe文件需要在打包后的目录中执行.

**Question:** 

- 在 Qt 于 Unity 双方建立 Socket 通信环境时，本地连接可以建立，但是读取数据时出现问题.

  > 继续摸索，实现对客户端发送字段数据的读写.

- 动画触发接口阻塞问题.

  > error: UnityMainThreadDispatcher 必须在主线程执行.
  >
  > 摸索动画接口函数.
  >
  > 设置一个消息队列，子线程接收到数据后添加至队列中.
  >
  > 主线程 Update 读取队列信息并播放动画.

  `注意:`

  1. 因为是同步数据，所以肯定每个时间单位都会发来一个事件，这样对于该队列的填充线程会一直排他性访问，主线程的动画调度怎么办？ **待解决**
  2. 通过任务队列调度动画，或者说通过动画切片来调度动画，没有办法实时同步，因为动画切片能够控制的只有动画播放的速度而不是模型的实时坐标(模型的实时坐标位置写入独自拿不来，理论可行，但是认知不足)，如果说控制两个状态的切换来实现模拟，为什么不直接一个行走动画切片来控制播放速度完成模拟呢？因为动画切片的转换，或者说过渡都是必须在上一动画切片结束才能开始过渡.
  3. 目前可能实现的较为准确的模拟是可以控制左右腿状态的不同播放速度，左腿动画一个实时速度，右腿动画一个实时速度.

- **动画切片的划分以及速度调整问题.**e

  > 1381 - 1390 迈左腿.
  >
  > 1390 - 1401 迈右腿.
  >
  > 设置 Wrap mode 为 once，因为 loop 会设置最后一帧将位置还原，导致动画不流畅.

- 通信走什么？

  > 双方沟通确定字段来传输.

- 同步数据的传输是在一次连接内完成？

- 接收数据的 while 循环一直在阻塞 Update 函数.

  > 数据传输没问题，但是 while 是在子线程中执行的，为什么会把主线程阻塞呢？

- 动画切片在播放时有可能被打断.

- 动画切片播放速度如何度量？

  > 动画切片在播放时可以设置速度，但是客户端发送速度值时应该怎么设置这个速度值，参照什么来设置？

- 动画切片播放速度的接口

  1. 控制 Animator 的播放速度.

     > animator.speed 直接设置整个 Animator 的播放速度.

  2. 改变状态下切片的播放速度.

```c# 
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class AnimationServer : MonoBehaviour
{
    private TcpListener tcpListener;
    private TcpClient connectedClient;

    public Animator animator;
    public int port = 8888;

    private void Start()
    {
        // 获取动画组件的引用
        animator = GetComponent<Animator>();

        // 启动服务器
        tcpListener = new TcpListener(IPAddress.Any, port);
        tcpListener.Start();
        Debug.Log("Server started. Waiting for client...");

        // 在新线程中监听客户端连接
        Thread listenThread = new Thread(ListenForClient);
        listenThread.Start();
    }

    private void ListenForClient()
    {
        connectedClient = tcpListener.AcceptTcpClient();
        Debug.Log("Client connected.");

        // 在新线程中监听客户端消息
        Thread receiveThread = new Thread(ReceiveMessages);
        receiveThread.Start();
    }

    private void ReceiveMessages()
    {
        byte[] buffer = new byte[1024];
        NetworkStream stream = connectedClient.GetStream();

        while (true)
        {
            try
            {
                // 读取客户端发送的数据
                int bytesRead = stream.Read(buffer, 0, buffer.Length);
                string message = Encoding.ASCII.GetString(buffer, 0, bytesRead);

                // 根据接收到的消息触发相应的模型动画
                switch (message)
                {
                    case "Attack":
                        PlayAnimation("Attack");
                        break;
                    case "Pissing":
                        PlayAnimation("Pissing");
                        break;
                    case "Death":
                        PlayAnimation("Death");
                        break;
                    // 添加其他需要处理的消息和相应的动画触发逻辑
                    default:
                        Debug.Log("Unknown message: " + message);
                        break;
                }
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
        // UnityMainThreadDispatcher.Instance.Enqueue(() =>
        // {
        //     animator.Play(animationName);
        // });
        Debug.Log("Error receiving message: " + animationName);
    }
}

```

v2.0 任务同步且线程安全队列实现主线程对动画切片的调用

``` C#
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

    // ConcurrentQueue Unity 内部已经实现了线程安全，无需自行加锁
    private ConcurrentQueue<string> animationQueue = new ConcurrentQueue<string>();
    // 保护共享资源的互斥锁
    private object queueLock = new object();

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
```

- 周四