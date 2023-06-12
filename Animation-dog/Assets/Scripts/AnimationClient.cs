using UnityEngine;
using System;
using System.Net.Sockets;
using System.Text;

public class AnimationClient : MonoBehaviour
{
    private TcpClient tcpClient;

    public string serverIP = "127.0.0.1";
    public int serverPort = 8888;

    private void Start()
    {
        ConnectToServer();
    }

    private void OnDestroy()
    {
        DisconnectFromServer();
    }

    private void ConnectToServer()
    {
        try
        {
            tcpClient = new TcpClient();
            tcpClient.Connect(serverIP, serverPort);
            Debug.Log("Connected to server.");
        }
        catch (Exception e)
        {
            Debug.Log("Failed to connect to server: " + e.Message);
        }
    }

    private void DisconnectFromServer()
    {
        if (tcpClient != null && tcpClient.Connected)
        {
            tcpClient.Close();
            Debug.Log("Disconnected from server.");
        }
    }

    public void SendAnimationCommand(string command)
    {
        if (tcpClient == null || !tcpClient.Connected)
        {
            Debug.Log("Not connected to the server.");
            return;
        }

        try
        {
            NetworkStream stream = tcpClient.GetStream();
            byte[] data = Encoding.ASCII.GetBytes(command);
            stream.Write(data, 0, data.Length);
            Debug.Log("Sent command: " + command);
        }
        catch (Exception e)
        {
            Debug.Log("Error sending command: " + e.Message);
        }
    }
}
