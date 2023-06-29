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

  > 1381 - 1391 迈左腿.
  >
  > 1391 - 1401 迈右腿.
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

# 2023.6.19

1. 明确需求

- 对接测试当前 dog demo 存在的问题以及需要改善的功能.

- 理清引入逐帧动画的目的.

  > 您好，我们这边需求是这样，我们客户端有狗运动的实时数据(但是这个数据只有一条腿的实时运动位置以及运动速度)，我们希望Unity端可以根据这个数据做一个实时的动画展示，保证迈腿的频率幅度时间和真实狗的相匹配. 你们那边可以根据客户端数据做到匹配吗.
  >
  > 目前我们的粗略的模拟方案就是设置了两种状态，迈左腿以及迈右腿动画状态，客户端发送指令控制迈左腿以及迈右腿，并且控制切片的播放速度来模拟，但是这样只能保证迈腿频次一致，很难保证实时
  >
  > 较好的方案是设置好骨骼绑定实时写入位置数据，但是比较尴尬的是我们目前只能监测一条腿关节处的位置与速度(坐标系将基于硬件设备)，其他骨骼位置数据需要基于这个作估算
  >
  > 您看您那边实现有什么更好的方案吗，或者是否能找到更好的映射呢

# 2023.6.20



- 那如果我抓取上一条指令与下一条指令的时间间隔呢？

- 相同指令频繁执行问题.

  > 归根结底是采样率问题，这几次相同指令均位于一次迈腿周期内.

1. 连续多次相同指令，视为一次迈腿，计算平均速度，预测迈腿所需时间并转换.

   > 平均速度不可取，正尝试取最大速度建立映射模型速度.

2. 只有一次的指令，视为一次迈腿，当前速度作为平均速度，计算迈腿所需时间并转换.

- 是否每次取两个，判断是否为相同，解决频繁执行问题.

- 采样滞后问题如何解决.

  > 每次send时并不发送数据，而仅仅判断迈腿方向，直到当前指令与缓存指令不同时，才发送缓存中的指令.
  >
  > 滞后处理.

- v 以什么为单位.

  > Client V m/s.
  >
  > 跑步机 3 km/h.

- 狗的视频和数据一致吗.

  > 一致.

- 动画播放卡顿是由客户端引起的

  > 客户端发送数据的频率.

- 服务端能不能接收到相同指令时，仅仅修改animator的播放速度？

  > 当Animator的播放速度足够细微.
  
- 视频播放数值与实际时间映射.

  > 30s <-> 990
  >
  > 1s <-> 33

- 要建立的映射究竟是何种映射.

  > 理解速度映射的关键是理解动画切片的速度意义.
  >
  > 动画切片的速度不具有运动意义，而仅仅代表一个倍率速度，控制切片的播放速率.
  >
  > 所以由真实速度映射过来的是一个失去运动意义的倍率速度.
  >
  > 由时间建立映射关系，我给与一个要求的切片播放时间，控制倍率以在规定时间内完成播放，这是关键.
  >
  > 所以问题就转化为了由当前的实际速度预测完成当前迈腿的时间.
  >
  > 首先根据速度的方向，可以获悉迈腿的方向，左腿或者右腿.
  >
  > 其次预测迈腿的时间，这个时间没有办法基于当前的速度值计算出来，所以我的想法是基于经验，设置梯度，参照最大速度来估测当前这个速度下的迈腿时间.

- 根据视频与速度值，建立五种初始映射模型

  > 因为狗的迈腿周期有一定规律性，理论上所有的周期建立映射模型即可完成转换.
  >
  > 目前建立五种观察效果.
  >
  > 肉眼很难区分
  >
  > 我想基于最大值，划定一个时间渐变区间，来建立映射模型.
  
- 所以我实际是基于峰值速度做得映射，而不是每一个速度做的预设

  > 因为如果使用每一个速度作映射，那么因为采样率的问题，这个无论什么样的采样率都无法避免，采样到的连续速度，可能处于同一个迈腿周期，也就是说可能迈左腿的一个周期内，就采集了三个速度，每个速度都映射过去，动画切片该如何播放，所以最好的方式是半个迈腿周期作一次映射，采集到的多个速度值采最大值作映射，真正映射的也不是速度，而是基于预测的迈腿所需要的时间，映射了动画切片实际播放的**倍率速度**.

- 映射速度的选取.

  > 目前基于峰值速度做的映射，原因是都试了一遍，峰值的映射速度更接近狗的跑步速度，可能因为它处于一个周期的中介.
  >
  > 因为非峰值速度太低了，映射过去播放的太慢.
  >
  > 其次，极值速度是唯一的呀，可以和当前周期建立唯一映射，其他速度一周周期内可能出现两次.
  >
  > 梯度也是从峰值开始递减.

- 梯度设置

  > 右腿 1 - 0.5
  >
  > 左腿 -0.6 - -0.2 
  >
  > 均设置4个梯度

| 左腿 | **峰值速度** | 迈腿时间 | 映射速度 | 迈腿时间2 | 映射速度2 |
| :--: | :----------: | :------: | :------: | :-------: | :-------: |
|      |   -0.8496    |   10z    |  1.3752  |   0.45    |   0.926   |
|      |   -0.5801    |   10z    |  1.3752  |   0.42    |  0.9921   |
|      |   -0.2961    |   12z    |  1.146   |    0.4    |   1.041   |
|      |   -0.3357    |   11z    |  1.2502  |   0.43    |   0.969   |
|      |   -0.3533    |   11z    |  1.2502  |    0.4    |   1.041   |
|      |              |          |          |           |           |
|      |              |          |          |           |           |
|      |              |          |          |           |           |
|      |              |          |          |           |           |

| 右腿 | **峰值速度** | 迈腿时间 | 映射速度 | 迈腿时间2 | 映射速度2 |
| :--: | :----------: | :------: | :------: | :-------: | :-------: |
|      |    0.8904    |   10z    |  1.3752  |   0.32    |   1.302   |
|      |     0.77     |   10z    |  1.3752  |   0.24    |   1.736   |
|      |    0.6428    |   11z    |  1.2502  |   0.22    |  1.8940   |
|      |    0.8726    |   11z    |  1.2502  |   0.24    |   1.736   |
|      |    0.7438    |   10z    |  1.3752  |   0.24    |   1.736   |
|      |              |          |          |           |           |
|      |              |          |          |           |           |
|      |              |          |          |           |           |
|      |              |          |          |           |           |

- 不能直接基于梯度算，有的采样点很少，那个并不是峰值.

  > 低于阈值的数据，采用默认梯度.

- 估量迈腿的时间不能基于视频.

- 脑电预测究竟预测的是什么.

  > 如果是传实时位置数据，还需要预测干什么?
  >
  > 除非基于脑电信号的预测计算出了下一帧的位置数据，实时写入没问题.
  >
  > 不然预测出来的还是这个传感器的速度.

# 2022.6.21

- 速度为0的点，是他的起始点吗？

  > 加速度的周期变化几乎是准确的，可以较精确的定义一次完整周期的起始点.
  >
  > 但是计算速度时解码的频率时10hz，与40hz的采样率相比会产生较大的误差.
  >
  > 那是否可以基于两次断定的起始/终点，判断误差的变化规律，从而减小误差呢？

- 断定一次完整周期的起始更容易一些.

  > 如果是这样子的话，我只需要保证一个完整周期的正确的，半个周期的速度折半执行不就行了？

- 映射预设模型的设置

  > 峰值速度对 <-> 周期时间 <-> 倍率速度
  >
  > 基于一个峰值定义映射可能存在问题，但是如果基于两个，半周期的峰值(一正一负)，来建立整个周期的映射呢？

- 速度积分问题.

  > 如果加速度是精确匹配的，那么速度的左右腿匹配是反的，也就是说当 v 解析的为负值时，迈腿为迈右腿.
  >
  > 要么以10hz的频率精确解出速度，以正负判断方向.
  >
  > 要么近似模拟，控制速度再1.3左右，一个周期0.6s左右
  >
  > 现在导致的问题是连频次都无法保证了，因为基于方向判定迈腿方向确定的周期于实际的周期是不符的.
  >
  > 为什么有时候会匹配，是因为预设模型将其控制在了1.3左右倍率的播放速度，于狗的几乎一致，但其实不是映射过去的.

- 每四个采样点为一个周期. **- 打灭**

  > 处于什么方向的迈腿周期.
  >
  > 周期的持续时间多久.

- 速度问题与传感器问题.

  > 加速度一直在波动，但是加速度周期与实际狗迈腿周期一致，所以加速度数据是认可的.
  >
  > 但是由加速度计算而得的速度值却在正负来回波动，由加速度曲线考虑是正常，但是实际应该不会有负值速度在迈右腿的过程中.
  >
  > 因此考虑是传感器的波动问题.

|           | 半周期起始 |      半周期终止      |      半周期时长      |      半周期起始      |    半周期终止    |     半周期时长     |    全周期时长    |
| --------- | :--------: | :------------------: | :------------------: | :------------------: | :--------------: | :----------------: | :--------------: |
| **A**     |    0/a     | 12.79 / a = 0.31975s | 12.79 / a = 0.31975s | 12.79 / a = 0.31975s |  25/a = 0.625s   | 12.21/a = 0.30525s |  25/a = 0.625s   |
| **V**     |   0.2/v    |   4.65/v = 0.465s    |   4.45/v = 0.445s    |   4.45/v = 0.445s    | 7.83/v = 0.783s  |  3.38/v = 0.338s   | 7.83/v = 0.783s  |
| **Error** |    0.2s    |                      |     **0.12525s**     |                      |                  |    **0.03275s**    |    **0.158s**    |
| **A**     |    25/a    |   38.68/a = 0.967s   |   13.68/a = 0.342s   |   38.68/a = 0.967s   | 50.9/a = 1.2725s |  12.22/a = 0.3055  | 25.9/a = 0.6475  |
| **V**     |   7.83/v   |     12/v = 0.12s     |   4.17/v = 0.417s    |     12/v = 0.12s     |  14.5/v = 1.45s  |   2.5/v = 0.25s    | 6.67/v = 0.667s  |
| **Error** |            |                      |      **0.075s**      |                      |                  |    **-0.0555s**    |   **0.0195s**    |
| **A**     |   50.9/a   |       64.83/a        |   13.93/a = 0.348s   |       64.83/a        |     77.97/a      | 13.14/a = 0.3285s  | 27.07/a = 0.677s |
| **V**     |   14.5/v   |       18.35/v        |   3.85/v = 0.385s    |       18.35/v        |      20.7/v      |  2.35/v = 0.235s   |  6.2/v = 0.62s   |
| **Error** |            |                      |      **0.037s**      |                      |                  |    **-0.0935s**    |    **-0.057**    |

# 2022.6.25

- 位置映射模型. 

  > 确定一个阈值来基于当前的位置值判定处于迈左腿周期还是迈右腿周期.
  >
  > 当判定迈腿周期成功后，基于位置峰值建立映射模型.

- 调档函问题.

- 模型.

- 位置数据的实际物理意义.

  > 做积分的时候考虑累加了嘛，考虑累加的话，那这个位移是不是本身就是想对于起始位置的位移.s
  >
  > 并不是实时的位置信息，而是相对于当前时刻的位置，0.1s的间隔内的位置变换信息.
  >
  > 速度也同理.

- 能否基于位置增量信息，计算得出实际的位置信息.

  > 转换计算而得的位置都将基于起始位置的相对偏移.
  >
  > 有了这个相对偏移，是否可以判断当前的迈腿周期.
  >
  > 我能基于加速度精确定义迈腿周期的时间点.
  >
  > 基于这个时间点，是否可以计算得出对应时间点的相对位移信息.
  >
  > 那这样是否可以找到一个阈值来界定左右腿.
  >
  > **狗的起始位置需要找到.**

- 狗的起始位置.

  > 时刻为0的数据并不是狗的起始位置，而是过了0.1秒积分后得到的相对全局位置的位移数据.

# 狗映射模型解决方案 - 初

1. 首先明确映射大致的解决思路

   > 映射分三级
   >
   > 倍率速度 <-> 播放时间 <-> 相对位移极值
   >
   > `注意:`
   >
   > 1. 因为现在的映射是因为时间紧张做的近似，因为极值虽然可以对应到一个周期，但是周期的长度与极值的大小并没有关联.
   > 2. 实际峰值出现的两个时间点作差，来计量上一个周期.

2. 其次，明确客户端如何控制指令的发送

   > 延时发送.
   >
   > 需要明确当前指令所处迈腿周期的类别，如果当前计算得到的相对位移 >-0.01 则是迈右腿.
   >
   > 当连续收到多组相同类别指令时，存储于缓存队列中，直到收到一组不同的类别指令，发送上一指令周期的极值位移.

   - 为什么阈值选择 -0.01 ，因为从曲线上断点，虽然半个周期断点可能不准，但是一整个周期而言准确率较高，该阈值也仅仅是估算阈值，不能仅仅通过这个判断所处迈腿周期类别，因此无论大于小于阈值，都有可能处于某一个迈腿周期中.
   - 为什么选择极值位移作映射，因为如果位移物理意义准确，是相对于全局的起始位置，那么迈左腿和迈右腿应该对应于两个极值，且一个极值可唯一对应一组半周期.

# 2022.6.26

- 封装绘图函数.

- 狗的左右腿有时卡顿问题.

  > 客户端的发送周期过长，服务端等待接收引起的播放卡顿.

- 如何根据位移波形来定义一个周期.

- 加速的一个周期与视频中的具体位置可能并不匹配.

  > 目前如何断点的呢？
  >
  > 首先根据加速度的波形，可以唯一明确的时迈腿的周期，不是半个周期而是整个周期时长.
  >
  > 但是周期的开始对应狗的哪个姿势并不能保证确定，目前根据视频姿势判断，可能加速度波动较大的对应迈右腿，加速度波动较小的对应迈左腿.

- 波峰之差，一个周期

- 波峰波谷之差，半个周期，峰->谷 ， 谷->峰

  > 不会实时，会有一个周期的延迟，因为这个指令的发送至少至少需要有两个周期的出现，才能发送上一周期较为精确的时间.

- 指令所属周期判断

  > 不再基于阈值判断哪一个指令属于哪一个周期.
  >
  > 而是指令直接入缓存，直到找到极值，作为一个周期.
  >
  > 连续的采样点，从波峰开始直至出现波谷的，为半个周期.
  >
  > 连续的采样点，从波谷开始直至出现波峰的，为半个周期.
  >
  > 不不不，还是判断一整个周期精确一点.

- 预处理

  > 起始位置需要是波峰或波谷，需要设置一定的偏移.

- 开始与终止

  > 开始只有半个周期，按默认播放，发送状态位？
  >
  > 如何终止，最后只有一个周期，按默认播放，发送状态位？

- 先保证IMU有百分之90的准确率，这样可以使得动画贴近于预测数据.



# 2023.6.27

- 周期个数需要计数

- 周期误差想要统计

- 狗的真实周期如何计算

- 既然已经是基于延时的，那还需要确定当前指令所属周期类别吗？

  > 已然不需要了.
  >
  > 本质上确定当前指令所属周期类别不也是为了确定一个周期的起始吗？
  >
  > 只需要确定如何界定一个周期就好了.

  1. 两次速度为0为一个周期
  2. 两次位移峰值/谷值出现为一个周期
  3. 周期间隔基于采样点，例如一周期含6个采样点，则周期时长为0.6s

- 为什么要设置偏移？

  > 因为0.1的采样率，我们的边界时间只能基于0.1s的单位，但是这样界定的范围太大，误差很大，所以设置一个偏移，使得播放更平稳一些

- 边界

  > 现在问题已经转换为了如何界定一整个周期，基于什么去界定，而不是判断当前指令所属的周期.

- 两次积分波形丢失的信息太多，做还原误差太大

- 基于连线与横轴的交点作为一整个迈腿周期

  > 以交点作为起始，交点做差得周期时间
  >
  > 半周期模糊处理得话就是均匀散开
  >
  > 精确处理就是第一次为零得点也去界定



# 2023.6.28

- 动画切片种类

  > 1. 初始迈右腿
  > 2. 初始迈左腿
  > 3. 左右腿交替迈腿
  > 4. 迈右腿结束恢复
  > 5. 迈左腿结束恢复
  > 6. 静止状态

- 没有做边界处理.

  > 因此目前只能起点恰好在当前数据处的波形映射效果会好一些.

- 映射模型数据偏移问题.

  > 起点并没有验证统一.

- 服务端卡顿问题.

  > 播放的不匹配有没有可能是服务端引起的？

- 之前的位移波形映射为什么会存在误差.

  > 因为之前的周期是基于采样点的，采样点是以0.1s为基本单位的，所以它界定的周期范围一般是0.5，0.6，0.7，0.1的单位有些大，会导致与真实周期存在误差，而这个误差会随着周期的增加累积.
  >
  > 能够抹消这个误差是因为不再使用采样点界定周期，而是位移曲线与y=0的交点，来界定一整个周期，注意是整个周期，而不是半个周期，因为只有右腿交点周期是准的，所以只以右腿所处周期与y=0的交点横坐标时间来界定周期时间.

- 重定向能力弱.

  > 因为没有处理边界问题，周期基本还是这样匹，但是代码的判定逻辑是基于616的加速度起点数据的，其他的加速度需要coding解决边界起点问题.

# 2023.6.29

- 视频的播放与指令的发送周期不同.

  > 视频播放的等待时差会累计，需要消除这个误差.

- 为什么基于事件更新的Animator切片播放状态并不准确.

  > 因为设置在 Enter 事件中更新 isPlaying 是错误的.
  >
  > 因为 Animator.play 的调度是基于调度器转到主线程执行的.
  >
  > 此时而上级主调函数中的 yield return new Waituntil 将和 Enter 事件函数不在一个调用堆栈中，就是说并不会先 Enter 事件偶=后 yield return. 
  >
  > 因此状态的更新只要进入 PlayAnimaton 函数，就要提前先更新，不管切片Enter事件触发没触发.
  >
  > 这样可以保证 yield return new Waituntil 使用的状态是正确的.
  >
  > 但是这种依赖于动画的方案时延很大.

- 先判断unity和真实狗从哪里不匹配的，在判断此时加速度是否和真实狗匹配，探究是否

- unity的偏差在+-0.01的量级

- 用一整个迈腿周期测算.

- 误差问题曲线方面又该如何解决，如何判定的准确率？

- 最后一个周期的边界可能有问题.

  > 如果是完整的周期没问题.
  >
  > 边界的可能会出现问题.

# 狗映射模型解决方案 - 终版

> 通过周期时间来建立映射.
>
> Unity 表现层动画播放倍率速度 <-> Unity 逻辑层指令等待时间 <-> Client 逻辑层指令周期时间 <-> 真实曲线周期时间.

- 曲线映射周期.

  > 首先需要根据积分后的以0.1s为间隔的**位移曲线**，准确界定迈腿周期.

- 客户端 逻辑层.

  > 以一个个的迈腿周期构建指令，指令包含迈腿的方向以及整个迈腿周期的时间.
  >
  > 客户端以 0.05s 的间隔发送构建好的指令，以便 Unity 端可以基于指令复现狗的状态.

- Unity 逻辑层.

  > Unity 端的本质工作是每隔一段时间执行一个指令，即每间隔一个迈腿周期，执行下一个迈腿指令.

- Unity 表现层.

  > 表现层及通过动画的形式来展示逻辑层的执行周期.

`注意:`

1. 将 Unity 划分为两个层级后，可以使得Unity指令的执行周期不依赖于动画切片，因为动画切片的播放收到帧率等等因素的影响，而逻辑层的周期时间是更加精准的.

   > 这就是为什么不通过判断切片是否执行完毕来播放下一切片，这个播放完毕所需要的时间要因为各种调度时延导致大于真实周期时间.
   >
   > 通过协程设置逻辑层的等待时间，精确控制指令的执行周期，表现层的动画可以打断，因为时间短，所以其实打断并不会造成卡顿或者少周期.

2. Unity 逻辑层的等待时间仍有正负 0.01s 的的微小误差，这个不可忽略.