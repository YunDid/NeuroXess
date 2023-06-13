
// using System.Collections;
// using System.Collections.Generic;
// using UnityEngine;
// using System;
// using System.Net;
// using System.Net.Sockets;
// using System.Text;
// using System.Threading;
// using System.Collections.Concurrent;
// using Newtonsoft.Json;

// public class AnimationServer : MonoBehaviour
// {
//     private TcpListener tcpListener;
//     private TcpClient connectedClient;

//     public Animator animator;
//     public int port = 8888;
//     public float anispeed;

//     private ConcurrentQueue<string> animationQueue = new ConcurrentQueue<string>();

//     private void Start()
//     {
//         animator = GetComponent<Animator>();
//         tcpListener = new TcpListener(IPAddress.Any, port);
//         tcpListener.Start();
//         Debug.Log("Server started. Waiting for client...");

//         System.Threading.Tasks.Task.Run(() => ListenForClient());
//     }

//     private void Update()
//     {
//         ProcessReceivedAnimations();
//     }

//     private void ListenForClient()
//     {
//         connectedClient = tcpListener.AcceptTcpClient();
//         Debug.Log("Client connected.");

//         System.Threading.Tasks.Task.Run(() => ReceiveMessages());
//     }

//     private void SendMessages() 
//     {
//         // Create a response object with the desired data
//         ReturnStateData returnStateData = new ReturnStateData();
//         returnStateData.Message = "This is the return state message.";

//         // Serialize the response object to JSON
//         string response = JsonConvert.SerializeObject(returnStateData);

//         // Send the response to the client
//         byte[] responseBuffer = Encoding.ASCII.GetBytes(response);
//         stream.Write(responseBuffer, 0, responseBuffer.Length);
//     }
//     private void ReceiveMessages()
//     {
//         byte[] buffer = new byte[1024];
//         NetworkStream stream = connectedClient.GetStream();

//         try
//         {
//             while (connectedClient.Connected)
//             {
//                 int bytesRead = stream.Read(buffer, 0, buffer.Length);
//                 if (bytesRead > 0)
//                 {
//                     string message = Encoding.ASCII.GetString(buffer, 0, bytesRead);
//                     Debug.Log("Received message: " + message);

//                     AnimationData animationData = JsonConvert.DeserializeObject<AnimationData>(message);

//                     // Process the animation data
//                     ProcessAnimationData(animationData);

//                     // Check if the client requested a return state
//                     if (animationData.NeedReturnStateFlag)
//                     {
//                        System.Threading.Tasks.Task.Run(() => SendMessages());
//                     }
//                 }
//                 else
//                 {
//                     break;
//                 }
//             }
//         }
//         catch (Exception e)
//         {
//             Debug.Log("Error receiving message: " + e.Message);
//         }

//         stream.Close();
//         connectedClient.Close();
//         Debug.Log("Client disconnected.");
//     }

//     private void ProcessReceivedAnimations()
//     {
//         while (animationQueue.TryDequeue(out string animationName))
//         {
//             PlayAnimation(animationName);
//         }
//     }

//     private void PlayAnimation(string animationName)
//     {
//         UnityMainThreadDispatcher.Instance.Enqueue(() =>
//         {
//             animator.Play(animationName);
//         });
//     }

//     private void ProcessAnimationData(AnimationData animationData)
//     {
//         // Process the animation data based on your requirements
//         string animationName = animationData.AnimationName;
//         float speed = animationData.Speed;

//         // Play the animation
//         PlayAnimation(animationName);
//         animator.speed = speed;
//     }
// }
