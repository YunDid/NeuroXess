using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;

public class AnimationServerCor : MonoBehaviour
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

        // 在协程中监听客户端连接
        StartCoroutine(ListenForClient());
    }

    private IEnumerator ListenForClient()
    {
        connectedClient = tcpListener.AcceptTcpClient();
        Debug.Log("Client connected.");

        // 获取网络流
        NetworkStream stream = connectedClient.GetStream();

        // 在协程中监听客户端消息
        yield return StartCoroutine(ReceiveMessages(stream));

        // 客户端断开连接后执行的代码
        stream.Close();
        connectedClient.Close();
        Debug.Log("Client disconnected.");
    }

    private IEnumerator ReceiveMessages(NetworkStream stream)
    {
        byte[] buffer = new byte[1024];

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
        yield return null;
    }

    private void PlayAnimation(string animationName)
    {
        // 在主线程中触发模型动画
        UnityMainThreadDispatcher.Instance.Enqueue(() =>
        {
            animator.Play(animationName);
        });
    }
}
