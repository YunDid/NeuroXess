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

# 2023.6.9

> 实现Unity可操纵三种状态响应的拉布拉多犬demo.

1. 模型获取.

   - 模型类型: 拉布拉多犬.

   - 模型状态: 除抬腿外，还有多种状态.

   - **模型动画切片类型存在问题，待解决.**

     > 对动画切片进行切割可能解决该问题.
     >
     > 已将行走动画切分为迈出左腿与卖出右腿.

2. 完成基本的 **Unity 事件**响应，触发动画.

   > 先通过键盘 Q,W,E 简单事件触发三种状态.
   >
   > 任何事件都可触发动画.

   - 通过 Animator 触发动画，并基于动画参数实现**状态转换.**

     > 问题在于这三种状态是否需要状态直接的切换，还是说仅仅想moba游戏一样直接触发技能那种就行.
     >
     > **状态只能触发一次，具化需求时需要看一下具体的接口下的动画切片调用逻辑**
  >
     > 接口改动，animator.Play(AnimationName,0,0); 设置播放起始点为0便可以重复播放.

   - 通过旧版 Animation 直接触发动画，而不是动画的切换. - 舍弃
   
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

- **动画切片的划分以及速度调整问题.**

  > 1381 - 1390 迈左腿.
  >
  > 1390 - 1401 迈右腿.
  >
  > 设置 Wrap mode 为 once，因为 loop 会设置最后一帧将位置还原，导致动画不流畅.
  >
  > 一帧 1/12 s.

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

# 2023.6.13

- 如何解决实时播放问题.

1. 队列无法解决实时问题，Sever 的动画播放始终是滞后的.

> 网络通信无法循环读取缓存区内容.
>
> 因为对消息队列的访问时排他性的，在 Update 与 ReadMessage 之间.
>
> 但是 ConcurrentQueue 却允许同时写入.
>
> 在这个场景中，使用队列几乎是线程安全的，因为Sever只管队头取Client只管队尾插，两者会存在什么冲突呢？

2. 基于事件信号实现实时通信.

   > 动画播放接口的调用可以是实时的，但是切片播放无法实时，会被打断.
   >
   > 若客户端发送的信号过快又该怎么办？

   - 动画切片的播放需要时间，客户端发送间隔也有一个时间量，当两者不统一时，怎么办，也就是说播一个动画切片的时候，客户端可能发了3个信号，如何处理.
   - 当客户端直接发多个数据的时候，Sever 调用接口的时机应该是实时的，但是切片的播放会有时间，因此再来一个事件会直接打断当前切片并播放另一个切片.

3. 那如果结合事件信号于与消息队列呢？

   > 

- 动画切片在播放时有可能被打断.

- 动画切片播放速度如何度量？

  > 动画切片在播放时可以设置速度，但是客户端发送速度值时应该怎么设置这个速度值，参照什么来设置？
  >
  > 速度为1时，1分钟150步.

- 为什么只有第一次传输的数据是消息，其余的均为空呢？**- 解决**

  > Server 一直在循环读取缓存区内容.
  >
  > 在客户端断开连接后，缓存区内容不会再作更新，不需要再循环读取了.

- ReceiveMessages 中 while 循环是不是不太合适 **- 解决**

  > 首先是客户端断开连接后，Sever端会一直循环读取缓存区，导致Sever无法关闭此次通信连接，第二个，当客户端很长一段时间没有发送数据的时候，Sever端也会一直读取空的缓存区.

  1. 在读取缓冲区前，先判断客户端是否已经断开连接，也就是每次循环前.

     > 这样子就不会导致客户端已经关闭还在循环读取.

  2. 读取缓冲区字节流，读取后并判断是否为空.

     > 是否为空目的是判断客户端是不是不发数据了，而不是缓存区是否为空.
     >
     > stream 对象内容是跟随客户端实时更新的，若客户端断开连接，则直接触发异常，Sever 端随之断开连接.
     >
     > 而且 stream.Read 是阻塞函数，不是阻塞主线程，而是 ReceiveMessages 线程，所以这个会一直等待客户端发送信息，若没有信息且客户端没有断开连接，则等待，若没有信息且客户端已经断开连接，则触发异常，Server 也随之断开连接.

  3. 为空可以添加延时代码来选择是否直接关闭连接或者延时等待一段时间后关闭.

     > 断开连接的设置不是很好，Sever 端是通过判断是否已经不发数据了，不发则直接断开，但是这个断开连接请求应该是客户端先发，**接口还不清楚.**

- 若客户端发送的是一个字段，该如何解析呢？**- 解决**

  > Tcp 网络通信传输基于字节数组，因此对应数据结构的发送需要基于协议去解析.
  >
  > Server 字段 <-> 字节流 <-> Client 字段
  >
  > 基于 Json 格式进行数据字段的传输.
  >
  > Unity 通过 UPM 安装 Json 依赖即可.

- 摄像机的移动. **- 解决**

  > 与 Unity 默认的摄像头控制逻辑相同.
  >
  > 鼠标右键 + Q W E A S D 控制摄像机移动.
  >
  > 鼠标右键控制摄像头旋转.
  >
  > 根据鼠标的当前位置或者键盘按下的轴值来控制旋转以及移动的增量.

- 接收到信号时发送当前状态，显示当前切片的播放状态. **- 解决** 

  > 设置发送字段，若标志位为true，则返回当前状态.
  >
  > 以json的格式传递.
  >
  > 一来一往方式，就是发送一次数据，请求返回一个状态，然后再发送？

- 添加一个退出程序的UI.

- 动画切片是否还有可以暴露的属性接口.

  > 先通过Json实现多字段传输的通道，再找.

- 多加几种状态.

  > 出现切片打断的情况时再找.

- 如何验证当前动画切片的播放是正常的？

  > 全局变量 isPlayingAnimation 检测当前是否在播放动画.

- 当前正在播放的和任务队列中存放的状态不一样. **- 解决**

  > 也就是当前播放的状态播放完后的下一个状态并不一定是现在客户端发的.
  >
  > 每播放一个切片，便把切片状态保留缓存.
  >
  > 注意哦，缓存在Server的更新是实时的，所以客户端一请求，直接发缓存即可.

- 在任意时刻发起状态请求时，我需要知道上一个动画切片是否播放完毕并且正常播放，播放完毕我直接播放下一个，没有播放完毕在添加控制逻辑，控制下一动画切片的播放. **- 解决** 

1. 通过事件订阅委托，状态播放开始或者完毕直接触发start与end事件通知，再更新状态.

2. 值得注意的是Animator中的每个状态都要订阅，否则只能监控一种状态的播放情况.

  

  1. 任意时刻，能够获取到是否正常播放(播放完毕且未被打断)

     > 现在虽然可以获取到当前动画切片的状态信息，但是没有办法通过当前方法判断动画切片是否结束，因此当切片结束转换到下一状态时，上一个状态的信息已经被新的状态信息覆盖，不会检测到 stateInfo.normalizedTime >= 1 的情况，只会显示下一状态的时间，上一个需要检测的状态stateInfo.normalizedTime 只会趋近于1
     >
     > 所以需要两个状态参数，判断当前状态名与上一状态名是否相同来判断是否结束. **- 舍弃**

  2. 控制逻辑的添加.

     > **仍通过打断事件通知，待完善.**

  3. 测试一下设置过渡，能否实时输出动画播放的状态信息.

     > 通过动画事件更新状态信息并实时返回.

  4. 区分开是 Animator 是否在播放还是 状态是否在播放.

     > 如何判断 Animator 是否在播放，注意空状态的使用.

  6. 任务队列依次弹出，动画播放问题.

     > 动画播放接口调用后，动画的播放和队列的弹出不是顺序同步的，就是说不是弹出一个播放一个，而是弹出多个，播放多个，一帧内如果没有间隔，动画的播放会被频繁的打断，导致只显示一个.

  7. 空动画状态问题. **- 解决**

     > 不为空状态附件事件行为组件，这样在进入空状态时，默认为无动画切片在播放，也不会触发动画事件.

  7. 动画播放一顿一顿的. **- 解决**

     > 两个动画切片的时长不同.
     >
     > 并且动画切换的时机没匹配.
     >
     > 目前是设置了Animator.speed 与 下一动画播放前的等待时间的映射关系，设置了对应的等待时间.

     ``` c# 
     // 等待动画播放完毕
     // yield return new WaitUntil(() => IsAnimationFinished());
     // 等待一段时间
     float time = 0.45f / (animation.Speed);
     ```

     

  9. 对于当前是否播放动画的状态判断需要更新，才能保证无闪顿动画切换.

  10. 使用队列处理的延时. **- 解决**

      > 必须，是必须等待上一个动画播放完毕再处理下一个.
      >
      > 不然会直接打断，动画接口的调用和动画的播放不是顺序同步的，动画会被第二次调用打断.

- 动画的过渡，不要复原到原始状态，而是保持不动，需要复原时才复原. **- 解决**

  > write defaut 关闭即可保持原状态.
  
- 状态变量的控制需要忽略掉 Idle 状态

- 需要在所有动画播放完毕后恢复 Idle 状态

- 第一帧动画播放需要设置过渡

v3.0 ReceiveMessages 阻塞问题完善.

``` c# 
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

    // private void ReceiveMessages()
    // {
    //     byte[] buffer = new byte[1024];
    //     NetworkStream stream = connectedClient.GetStream();

    //     while (true)
    //     {
    //         try
    //         {
    //             // 清空缓冲区
    //             // Array.Clear(buffer, 0, buffer.Length);
                
    //             // 读取客户端发送的数据
    //             int bytesRead = stream.Read(buffer, 0, buffer.Length);
    //             string message = Encoding.ASCII.GetString(buffer, 0, bytesRead);

    //             Debug.Log("Test log animationName: " + message);

    //             // // 根据接收到的消息触发相应的模型动画
    //             // switch (message)
    //             // {
    //             //     case "Attack":
    //             //         PlayAnimation("Attack");
    //             //         break;
    //             //     case "Pissing":
    //             //         PlayAnimation("Pissing");
    //             //         break;
    //             //     case "Death":
    //             //         PlayAnimation("Death");
    //             //         break;
    //             //     // 添加其他需要处理的消息和相应的动画触发逻辑
    //             //     default:
    //             //         Debug.Log("Unknown message: " + message);
    //             //         break;
    //             // }

    //             // 将接收到的动画事件添加到队列中
    //             if(message != "")
    //                 animationQueue.Enqueue(message);
    //         }
    //         catch (Exception e)
    //         {
    //             Debug.Log("Error receiving message: " + e.Message);
    //             break;
    //         }
    //     }

    //     stream.Close();
    //     connectedClient.Close();
    //     Debug.Log("Client disconnected.");
    // }
 
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
                    string message = Encoding.ASCII.GetString(buffer, 0, bytesRead);

                    Debug.Log("Test log animationName: " + message);

                    // 将接收到的动画事件添加到队列中
                    animationQueue.Enqueue(message);
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

v4.0 网络字段通过Json传输.

``` c#
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
        public string AnimationName { get; set; }
        public float Speed { get; set; }
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
```

v4.0.1 添加服务端发送数据的接口.

``` c# 
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
```

Qt 客户端

``` c# 
//#include <QCoreApplication>
//#include <QTcpSocket>
//#include <QJsonDocument>
//#include <QJsonObject>
//#include <QTimer>

////void SendAnimationCommand(const QString& command)
////{
////    QTcpSocket socket;
////    socket.connectToHost("127.0.0.1", 8888);
////    int count = 0;

////    if (socket.waitForConnected())
////    {
////        QByteArray data = command.toUtf8();
////        QTimer* timer = new QTimer(); // 使用 QTimer 对象
////        int delay = 1000; // 设置延迟时间为 1 秒

//////        while (true) {

//////            count++;
//////            timer->setInterval(delay);
//////            socket.write(data);
//////            socket.waitForBytesWritten();
//////            if(count == 10)
//////                break;
//////        }
////        socket.write(data);
////        socket.waitForBytesWritten();
////        socket.disconnectFromHost();
////        while(true) {

////        }
////    }
////    else
////    {
////        qDebug() << "Failed to connect to server.";
////    }
////}


//void SendAnimationCommand(const QJsonObject& commandObject)
//{
//    QTcpSocket socket;
//    socket.connectToHost("127.0.0.1", 8888);

//    if (socket.waitForConnected())
//    {
//        QJsonDocument jsonDoc(commandObject);
//        QByteArray jsonData = jsonDoc.toJson();

//        socket.write(jsonData);
//        socket.waitForBytesWritten();
//        socket.disconnectFromHost();
//    }
//    else
//    {
//        qDebug() << "Failed to connect to server.";
//    }
//}

//int main(int argc, char *argv[])
//{
//    QCoreApplication a(argc, argv);

//    QJsonObject commandObject;
//    commandObject["AnimationName"] = "LeftLeg";
//    commandObject["Speed"] = 5;
//    // 添加其他字段...

//    SendAnimationCommand(commandObject);

//    return a.exec();
//}

#include <QCoreApplication>
#include <QTcpSocket>
#include <QTimer>
#include <QDebug>
#include <QJsonDocument>
#include <QJsonObject>

struct AnimationData
{
    QString AnimationName;
    float Speed;
    bool NeedReturnStateFlag;
};

struct ReturnStateData
{
    QString AnimationName;
    float Speed;
    bool IsCorrect;
};

void ReceiveAnimationCommand(QTcpSocket& socket);

void SendAnimationCommand(const AnimationData& animationData)
{
    QTcpSocket socket;
    socket.connectToHost("127.0.0.1", 8888);

    if (socket.waitForConnected())
    {
        // Serialize the animation data to JSON
        QJsonObject jsonObject;
        jsonObject["AnimationName"] = animationData.AnimationName;
        jsonObject["Speed"] = animationData.Speed;
        jsonObject["NeedReturnStateFlag"] = animationData.NeedReturnStateFlag;

        QJsonDocument jsonDocument(jsonObject);
        QByteArray jsonData = jsonDocument.toJson();

        // Send the JSON data to the server
        socket.write(jsonData);
        socket.waitForBytesWritten();

        // Check if the client expects a return state
        if (animationData.NeedReturnStateFlag)
        {
            ReceiveAnimationCommand(socket);
        }
    }
    else
    {
        qDebug() << "Failed to connect to server.";
    }
}

void ReceiveAnimationCommand(QTcpSocket& socket)
{
    // Wait for the server's response
    socket.waitForReadyRead();

    // Read the response from the server
    QByteArray responseData = socket.readAll();
    QJsonDocument responseJson = QJsonDocument::fromJson(responseData);
    QJsonObject responseObj = responseJson.object();

    // Deserialize the response data
    ReturnStateData returnStateData;
    returnStateData.AnimationName = responseObj["AnimationName"].toString();
    returnStateData.Speed = responseObj["Speed"].toInt();
    returnStateData.IsCorrect = responseObj["IsCorrect"].toBool();

    // Process the returned state data as needed
    qDebug() << "Received return state message: " << returnStateData.AnimationName;
    qDebug() << "Received return state message: " << returnStateData.Speed;
    qDebug() << "Received return state message: " << returnStateData.IsCorrect;
}

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);

    AnimationData animationData;
    animationData.AnimationName = "LeftLeg";
    animationData.Speed = 5.0;
    animationData.NeedReturnStateFlag = true;

    SendAnimationCommand(animationData);

    return a.exec();
}

```

# 2023.6.15

v4.0 连续传输数据版

- Unity Server

``` c# 
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

    // 检测动画状态是否播放完毕
    bool IsAnimationFinished()
    {
        return !isPlaying;
    }

}
```

- Qt Client

``` c++ 
//#include <QCoreApplication>
//#include <QTcpSocket>
//#include <QJsonDocument>
//#include <QJsonObject>
//#include <QTimer>

////void SendAnimationCommand(const QString& command)
////{
////    QTcpSocket socket;
////    socket.connectToHost("127.0.0.1", 8888);
////    int count = 0;

////    if (socket.waitForConnected())
////    {
////        QByteArray data = command.toUtf8();
////        QTimer* timer = new QTimer(); // 使用 QTimer 对象
////        int delay = 1000; // 设置延迟时间为 1 秒

//////        while (true) {

//////            count++;
//////            timer->setInterval(delay);
//////            socket.write(data);
//////            socket.waitForBytesWritten();
//////            if(count == 10)
//////                break;
//////        }
////        socket.write(data);
////        socket.waitForBytesWritten();
////        socket.disconnectFromHost();
////        while(true) {

////        }
////    }
////    else
////    {
////        qDebug() << "Failed to connect to server.";
////    }
////}


//void SendAnimationCommand(const QJsonObject& commandObject)
//{
//    QTcpSocket socket;
//    socket.connectToHost("127.0.0.1", 8888);

//    if (socket.waitForConnected())
//    {
//        QJsonDocument jsonDoc(commandObject);
//        QByteArray jsonData = jsonDoc.toJson();

//        socket.write(jsonData);
//        socket.waitForBytesWritten();
//        socket.disconnectFromHost();
//    }
//    else
//    {
//        qDebug() << "Failed to connect to server.";
//    }
//}

//int main(int argc, char *argv[])
//{
//    QCoreApplication a(argc, argv);

//    QJsonObject commandObject;
//    commandObject["AnimationName"] = "LeftLeg";
//    commandObject["Speed"] = 5;
//    // 添加其他字段...

//    SendAnimationCommand(commandObject);

//    return a.exec();
//}

#include <QCoreApplication>
#include <QTcpSocket>
#include <QTimer>
#include <QDebug>
#include <QJsonDocument>
#include <QJsonObject>

struct AnimationData
{
    QString AnimationName;
    float Speed;
    bool NeedReturnStateFlag;
};

struct ReturnStateData
{
    QString AnimationName;
    // 当前动画的播放速度
    float Speed;
    bool IsCorrect;
    // 检测当前是否有动画在播放
    bool IsPlaying;
    // 检测动画是否播放完毕
    bool IsEndPlaying;
    // 检测动画是否被打断
    bool IsInterrupted;
};

void ReceiveAnimationCommand(QTcpSocket& socket);

void SendAnimationCommand(const AnimationData& animationData,QTcpSocket& socket)
{

    if (socket.waitForConnected())
    {
        // 序列化数据
        QJsonObject jsonObject;
        jsonObject["AnimationName"] = animationData.AnimationName;
        jsonObject["Speed"] = animationData.Speed;
        jsonObject["NeedReturnStateFlag"] = animationData.NeedReturnStateFlag;

        QJsonDocument jsonDocument(jsonObject);
        QByteArray jsonData = jsonDocument.toJson();

        // 发送 Json 数据
        socket.write(jsonData);
        socket.waitForBytesWritten();

        // 检查状态位，若需要返回状态信息，则阻塞等待信息
        if (animationData.NeedReturnStateFlag)
        {
            ReceiveAnimationCommand(socket);
        }
    }
    else
    {
        qDebug() << "Failed to connect to server.";
    }
}

void ReceiveAnimationCommand(QTcpSocket& socket)
{
    // 等待服务端响应
    socket.waitForReadyRead();

    // 读取响应
    QByteArray responseData = socket.readAll();
    QJsonDocument responseJson = QJsonDocument::fromJson(responseData);
    QJsonObject responseObj = responseJson.object();

    // 反序列化数据
    ReturnStateData returnStateData;
    returnStateData.AnimationName = responseObj["AnimationName"].toString();
    // 强转int不对，先赋值整数测，或者字段类型改为daouble
    returnStateData.Speed = responseObj["Speed"].toInt();
    returnStateData.IsCorrect = responseObj["IsCorrect"].toBool();

    // debug
    qDebug() << "Received return state AnimationName: " << returnStateData.AnimationName;
    qDebug() << "Received return state Speed: " << returnStateData.Speed;
    qDebug() << "Received return state IsCorrect: " << returnStateData.IsCorrect;
    qDebug() << "Received return state IsEndPlaying: " << returnStateData.IsEndPlaying;
    qDebug() << "Received return state IsInterrupted: " << returnStateData.IsInterrupted;
    qDebug() << "Received return state IsPlaying: " << returnStateData.IsPlaying;
}

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);

    AnimationData animationData;
    animationData.AnimationName = "LeftLeg";
    animationData.Speed = 1.0f;
    animationData.NeedReturnStateFlag = true;

    QTcpSocket socket;
    socket.connectToHost("127.0.0.1", 8888);

    int count = 0;

    while(true)
    {

        // 播放 20 次动画

        if(count % 2 == 0)
            animationData.AnimationName = "LeftLeg";
        else
            animationData.AnimationName = "RightLeg";

        SendAnimationCommand(animationData, socket);

        if (count == 20)
            break;

        count++;
    }

    return a.exec();
}

```

