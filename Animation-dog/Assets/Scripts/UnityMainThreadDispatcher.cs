using System;
using UnityEngine;

public class UnityMainThreadDispatcher : MonoBehaviour
{
    private static UnityMainThreadDispatcher instance = null;

    private static readonly object lockObject = new object();
    private static bool applicationIsQuitting = false;

    private readonly System.Collections.Generic.Queue<Action> actionQueue = new System.Collections.Generic.Queue<Action>();

    public static UnityMainThreadDispatcher Instance
    {
        get
        {
            if (applicationIsQuitting)
            {
                Debug.LogWarning("[UnityMainThreadDispatcher] Instance already destroyed on application quit.");
                return null;
            }

            lock (lockObject)
            {
                if (instance == null)
                {
                    var gameObject = new GameObject("[UnityMainThreadDispatcher]");
                    instance = gameObject.AddComponent<UnityMainThreadDispatcher>();
                    DontDestroyOnLoad(gameObject);
                }

                return instance;
            }
        }
    }

    private void OnDestroy()
    {
        applicationIsQuitting = true;
    }

    public void Enqueue(Action action)
    {
        lock (actionQueue)
        {
            actionQueue.Enqueue(action);
        }
    }

    private void Update()
    {
        lock (actionQueue)
        {
            while (actionQueue.Count > 0)
            {
                Action action = actionQueue.Dequeue();
                action.Invoke();
            }
        }
    }
}
